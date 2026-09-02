import asyncio
import datetime
import gzip
import json
import logging
import os
import random
import time
import uuid

import aiohttp
import boto3
import polars as pl
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
handle = "tesco_api"
logger = logging.getLogger(handle)

with open("graphql_query.txt") as file:
    TESCO_GRAPHQL_QUERY = file.read().rstrip()

BUCKET = "ie-supermarket-data"

# --- Rate limiting -----------------------------------------------------------
# 2026-08-09 Tesco put Akamai Rate Controls in front of xapi.tesco.com. The
# measured sustainable knee is ~2.5 req/s *in aggregate* across every container,
# and bursty concurrency trips it harder than even pacing at the same mean rate
# (see docs/tesco-429-incident.md). So: pace every request start through a
# single token-bucket-ish pacer at a target aggregate rate divided evenly over
# the chunk count, and honour Retry-After with bounded exponential backoff.
TARGET_AGGREGATE_RPS = float(os.environ.get("TESCO_TARGET_RPS", "2.0"))
# Only a connection bound now — the pacer, not this, controls request rate. It
# needs to be >= target_rps_per_container * request_latency (~2.5 s for a full
# PDP GraphQL response) so a slow response can't drag the effective rate below
# the pacer target; it never bursts because the pacer still spaces every start.
CONCURRENT_REQUESTS = int(os.environ.get("TESCO_CONCURRENCY", "6"))
MAX_ATTEMPTS = int(os.environ.get("TESCO_MAX_ATTEMPTS", "6"))
BACKOFF_CAP_SECONDS = 60.0
DELAY_BETWEEN_BATCHES = 2

# Smoke-test knobs. OUTPUT_PREFIX keeps a test run out of the production
# raw/tesco/{date}/ partition that dbt reads; MAX_PRODUCTS caps the pass.
OUTPUT_PREFIX = os.environ.get("TESCO_OUTPUT_PREFIX", "raw/tesco").rstrip("/")
MAX_PRODUCTS = int(os.environ.get("TESCO_MAX_PRODUCTS", "0"))  # 0 = no cap

API_KEY = "TvOSZJHlEk0pjniDGQFAc9Q59WGAR4dA"
USER_AGENT_STRINGS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
]

TESCO_IDS = (
    pl.read_parquet(
        f"s3://{BUCKET}/raw/tesco/ids/latest/tesco_product_ids.parquet",
        storage_options={"aws_region": "eu-west-1"},
    )
    .get_column("id")
    .cast(pl.String)
    .unique()
    .sort()
    .to_list()
)
logger.info(f"Loaded {len(TESCO_IDS)} tesco product IDs from S3")


class RatePacer:
    """Spaces out request *starts* to a target rate, shared across all workers.

    Evenly-paced requests survived ~3 req/s at 2% loss where concurrency-5
    bursts failed 33% at the same mean rate, so the pacer gates every request
    (first attempt or retry) rather than relying on a semaphore + fixed sleep.
    """

    def __init__(self, rate_per_second: float):
        self._min_interval = 1.0 / rate_per_second if rate_per_second > 0 else 0.0
        self._next_slot = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            slot = max(now, self._next_slot)
            # small +/- jitter so retries across workers don't re-synchronise
            self._next_slot = slot + self._min_interval * random.uniform(0.85, 1.15)
        wait = slot - time.monotonic()
        if wait > 0:
            await asyncio.sleep(wait)


def get_headers():
    trace_id = str(uuid.uuid4())
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "language": "en-IE",
        "origin": "https://www.tesco.ie",
        "referer": "https://www.tesco.ie/",
        "region": "IE",
        "user-agent": random.choice(USER_AGENT_STRINGS),
        "x-apikey": API_KEY,
        "traceid": f"{trace_id}:{uuid.uuid4()}",
        "trkid": trace_id,
    }


def build_payload(tpnc: str) -> list:
    return [
        {
            "operationName": "GetProduct",
            "variables": {
                "includeVariations": True,
                "includeFulfilment": True,
                "markRecentlyViewed": False,
                "includeMatchingProducts": True,
                "tpnc": tpnc,
                "skipReviews": True,
                "offset": 0,
                "count": 10,
                "sellersType": "ALL",
                "sellerTypeForVariations": "TOP",
                "productReviewsNodeMaxTimeout": 380,
            },
            "extensions": {"mfeName": "mfe-pdp"},
            "query": TESCO_GRAPHQL_QUERY,
        }
    ]


def load_checkpoint(chunk_id: int, folder_date: str) -> set[str]:
    s3 = boto3.client("s3")
    key = f"{OUTPUT_PREFIX}/{folder_date}/checkpoints/chunk_{chunk_id}.json"
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        data = json.loads(obj["Body"].read())
        return set(data["processed_ids"])
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return set()
        raise


def save_checkpoint(chunk_id: int, folder_date: str, processed_ids: list[str]) -> None:
    s3 = boto3.client("s3")
    key = f"{OUTPUT_PREFIX}/{folder_date}/checkpoints/chunk_{chunk_id}.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps({"processed_ids": processed_ids}),
        ContentType="application/json",
    )


def delete_checkpoint(chunk_id: int, folder_date: str) -> None:
    s3 = boto3.client("s3")
    key = f"{OUTPUT_PREFIX}/{folder_date}/checkpoints/chunk_{chunk_id}.json"
    try:
        s3.delete_object(Bucket=BUCKET, Key=key)
    except Exception:
        pass


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None


_RATE_LIMIT_MARKERS = ("too many requests", "rate limit", "ratelimit", "throttl")
_NOT_FOUND_MARKERS = ("not-found", "not found", "notfound")
# Transient Tesco-backend GraphQL errors (HTTP 200 body): worth retrying within
# the request loop, but NOT worth keeping the checkpoint / forcing a Batch retry
# for if they persist — unlike a 429, they won't clear by re-running the container.
_TRANSIENT_MARKERS = (
    "aborted",
    "timeout",
    "timed out",
    "temporarily",
    "try again",
    "internal server error",
    "service unavailable",
    "bad gateway",
)


def _classify_200(body) -> tuple[str, object]:
    """Map a 200 GraphQL body to (status, payload).

    Tesco answers some requests with HTTP 200 and a GraphQL-error body, and those
    errors are a mix of things we must treat very differently:
      - "ok"        -> payload is the product dict, or None when the product is
                       legitimately absent (data.product is null).
      - "absent"    -> a "product-not-found" GraphQL error: a stale ID from the
                       slower ID-refresh cycle, benign. Recorded like an absent
                       product (data null, no error) so it doesn't inflate the
                       scrape-error-rate monitor or get retried forever.
      - "ratelimit" -> a rate-limit rejection at the GraphQL layer (e.g.
                       {"message":"Too many requests","extensions":{"http":{"status":429}}})
                       or a malformed body. Retried in-loop AND, if it persists,
                       left uncheckpointed for a Batch-level retry.
      - "transient" -> a transient backend error ("operation was aborted", 5xx-ish
                       messages). Retried in-loop, but a permanent failure if it
                       persists (re-running the container won't help).
      - "error"     -> any other GraphQL error — surfaced immediately so a real
                       regression is visible.
    payload is the product (ok) / None (absent) / a short reason string otherwise.
    """
    try:
        entry = body[0]
    except KeyError, IndexError, TypeError:
        return "ratelimit", "malformed body (no entry[0])"

    errors = entry.get("errors") if isinstance(entry, dict) else None
    if errors:
        first = errors[0] if isinstance(errors, list) and errors else {}
        first = first if isinstance(first, dict) else {}
        msg = str(first.get("message", "unknown"))
        low = msg.lower()
        http_status = (first.get("extensions") or {}).get("http", {}).get("status")
        if http_status == 429 or any(m in low for m in _RATE_LIMIT_MARKERS):
            return "ratelimit", f"GraphQL 429: {msg}"
        if any(m in low for m in _NOT_FOUND_MARKERS):
            return "absent", None
        if http_status in (500, 502, 503, 504) or any(m in low for m in _TRANSIENT_MARKERS):
            return "transient", f"GraphQL transient: {msg}"
        return "error", f"GraphQL error: {msg}"

    if isinstance(entry, dict) and "data" in entry:
        data = entry.get("data") or {}
        return "ok", data.get("product")

    return "ratelimit", "malformed body (no data / no errors key)"


def _settled(tpnc: str, data, error: str | None, retryable: bool) -> dict:
    return {"tpnc": tpnc, "data": data, "error": error, "retryable": retryable}


async def fetch_product(
    session: aiohttp.ClientSession,
    tpnc: str,
    semaphore: asyncio.Semaphore,
    pacer: RatePacer,
) -> dict:
    """Fetch one product, retrying rate-limit / transient failures.

    Returns {tpnc, data, error, retryable}. `retryable` is True only when the
    unsettled state is a rate-limit / connectivity failure that a fresh Batch
    attempt could clear — the caller then leaves the tpnc out of the checkpoint
    and keeps the checkpoint so `attempts: 2` re-fetches exactly those.
    """
    last_error = "no attempt made"
    last_retryable = True
    for attempt in range(MAX_ATTEMPTS):
        await pacer.acquire()
        retry_after: float | None = None
        try:
            async with semaphore:
                async with session.post(
                    "https://xapi.tesco.com/",
                    headers=get_headers(),
                    json=build_payload(tpnc),
                ) as response:
                    if response.status == 200:
                        status, payload = _classify_200(await response.json())
                        if status == "ok":
                            return _settled(tpnc, payload, None, False)
                        if status == "absent":
                            return _settled(tpnc, None, None, False)
                        if status == "error":
                            return _settled(tpnc, None, payload, False)
                        # "ratelimit" / "transient" -> fall through to backoff
                        last_error = payload
                        last_retryable = status == "ratelimit"
                    elif response.status == 429:
                        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
                        last_error, last_retryable = "HTTP 429", True
                    elif response.status in (500, 502, 503, 504):
                        last_error, last_retryable = f"HTTP {response.status}", True
                    else:
                        # 4xx other than 429 — permanent per-product failure
                        return _settled(tpnc, None, f"HTTP {response.status}", False)
        except (aiohttp.ClientError, TimeoutError) as e:
            last_error, last_retryable = f"{type(e).__name__}: {e}", True

        if attempt < MAX_ATTEMPTS - 1:
            base = retry_after if retry_after is not None else 1.0
            backoff = min(base * (2**attempt), BACKOFF_CAP_SECONDS)
            await asyncio.sleep(backoff + random.uniform(0, base))

    return _settled(tpnc, None, last_error, last_retryable)


async def fetch_all_products(
    product_ids: list[str], chunk_id: int, folder_date: str, timestamp: str
) -> dict[str, int]:
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    pacer = RatePacer(TARGET_AGGREGATE_RPS / max(total_chunks, 1))
    s3 = boto3.client("s3")
    timeout = aiohttp.ClientTimeout(total=90, connect=15)
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS, ttl_dns_cache=300)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [fetch_product(session, tpnc, semaphore, pacer) for tpnc in product_ids]
        counts = {"ok": 0, "absent": 0, "failed": 0, "retryable": 0}
        processed_ids: list[str] = []
        batch_size = 100
        for batch_num, i in enumerate(range(0, len(tasks), batch_size)):
            batch = tasks[i : i + batch_size]
            batch_results = await asyncio.gather(*batch)

            batch_filename = f"tesco_raw_{timestamp}_chunk{chunk_id}_batch{batch_num:04d}.jsonl.gz"
            tmp_path = f"/tmp/{batch_filename}"
            with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
                for result in batch_results:
                    # persist only the wire fields; `retryable` is control-plane
                    f.write(json.dumps({k: result[k] for k in ("tpnc", "data", "error")}) + "\n")
            s3.upload_file(tmp_path, BUCKET, f"{OUTPUT_PREFIX}/{folder_date}/{batch_filename}")

            for r in batch_results:
                if r["error"] is not None:
                    counts["failed"] += 1
                    if r["retryable"]:
                        counts["retryable"] += 1
                elif r["data"] is None:
                    counts["absent"] += 1
                else:
                    counts["ok"] += 1
            # Checkpoint only settled tpncs — a transient failure is left out so a
            # Batch retry re-fetches it instead of the checkpoint poisoning the retry.
            processed_ids.extend(r["tpnc"] for r in batch_results if not r["retryable"])
            save_checkpoint(chunk_id, folder_date, processed_ids)
            logger.info(
                f"Processed {min(i + batch_size, len(tasks))}/{len(tasks)} products "
                f"(ok={counts['ok']} absent={counts['absent']} failed={counts['failed']})"
            )
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)
        return counts


chunk_id = int(os.environ["CHUNK_ID"])
total_chunks = int(os.environ["TOTAL_CHUNKS"])
logger.info(f"Scraping chunk {chunk_id}/{total_chunks}")

now = datetime.datetime.now(tz=datetime.UTC)
folder_date = now.strftime("%Y-%m-%d")
timestamp = now.strftime("%Y%m%d_%H%M%S")

chunk_size = len(TESCO_IDS) // total_chunks
start = chunk_id * chunk_size
end = start + chunk_size if chunk_id < total_chunks - 1 else len(TESCO_IDS)
product_ids = TESCO_IDS[start:end]

already_processed = load_checkpoint(chunk_id, folder_date)
if already_processed:
    logger.info(f"Resuming from checkpoint: {len(already_processed)} already processed")
    product_ids = [tpnc for tpnc in product_ids if tpnc not in already_processed]

if MAX_PRODUCTS:
    product_ids = product_ids[:MAX_PRODUCTS]
    logger.info(f"TESCO_MAX_PRODUCTS set — capping this run at {len(product_ids)} products")

logger.info(
    f"Fetching {len(product_ids)} products (chunk {start}:{end}); "
    f"pacer target {TARGET_AGGREGATE_RPS / max(total_chunks, 1):.2f} req/s per container, "
    f"writing to s3://{BUCKET}/{OUTPUT_PREFIX}/{folder_date}/"
)

counts = asyncio.run(fetch_all_products(product_ids, chunk_id, folder_date, timestamp))

logger.info(
    f"Done chunk {chunk_id}: ok={counts['ok']} absent={counts['absent']} "
    f"failed={counts['failed']} (of which retryable={counts['retryable']})"
)
if counts["retryable"]:
    # Leave the checkpoint in place so a Batch retry resumes on the unsettled tpncs.
    logger.warning(
        f"{counts['retryable']} products still failing after {MAX_ATTEMPTS} attempts — "
        f"keeping checkpoint for chunk {chunk_id} so a retry can pick them up"
    )
else:
    delete_checkpoint(chunk_id, folder_date)
logger.info(f"Completed chunk {chunk_id}")
