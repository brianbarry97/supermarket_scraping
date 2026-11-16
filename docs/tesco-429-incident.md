# Tesco scraper — Akamai rate-limiting incident (2026-08-09 onward)

**Update 2026-10-28:** the Tesco scraper has since moved onto `scraper_common/` with request pacing, backoff
and a data-quality gate (see `docs/scraper_data_quality.md`), and the chunk run summaries for 2026-10-22
to 2026-10-26 report every chunk `ok`. Whether the underlying Akamai rate control is lifted or just
respected is not re-investigated here. The rest of this document is the original analysis and is kept
as history.

**Original status:** open, unfixed as of 2026-09-02. Not yet triaged into a work item — this document
exists so a fresh session can pick it up with full context.

**Scope note:** discovered while auditing category data for the SuperValu taxonomy consolidation.
It is a separate workstream and none of the fixes below have been implemented.

---

## TL;DR

- On the night of **2026-08-08 → 2026-08-09**, Tesco placed **Akamai Rate Controls** in front of
  `xapi.tesco.com`. A single clean step, not a drift. Nothing changed on our side.
- Since then, **~70% of every daily Tesco scrape is lost**: ~56% as `HTTP 429`, ~14% as a "silent"
  mode (`data` and `error` both NULL) that is *also* rate-limiting arriving via an HTTP 200
  GraphQL-error body.
- Failures **rotate** day to day, so a multi-day union recovers to ~67%, but a ~33% tail
  (3,291 tpncs hard-429 on every attempt in a 4-day sample) resists backfill.
- `tesco/tesco_api.py` has **no retry/backoff of any kind** and discards the `Retry-After: 1`
  header the server sends.
- Downstream: `scd_product_prices` has gaps **and wrong change-dates** since 08-09;
  `int_all_supermarket_products` writes a different ~30% of Tesco each run.

Raw per-date history: [`tesco-429-error-rate-history.tsv`](./tesco-429-error-rate-history.tsv)
(all 103 partitions, no sampling).

---

## 1. Error-rate history — one clean step on 2026-08-09

Full sweep of all 103 date partitions (every `*.jsonl.gz` read via DuckDB `read_json` with
`ignore_errors=false`; row totals verified against 2026-09-01: 19,952 / 11,145 / 2,866).

| date | total | ok | ok% | HTTP 429 | 429% | silent (data+error NULL) | silent% |
|---|---|---|---|---|---|---|---|
| 2026-02-01 … 2026-08-08 | ~19.9k/day | ~100% | 99.6–100% | 0 | 0.0% | 0–74 | ≤0.4% |
| 2026-08-07 | 19,952 | 19,951 | 100.0% | 0 | 0.0% | 1 | 0.0% |
| **2026-08-08** | 19,952 | 19,951 | 100.0% | 0 | 0.0% | 1 | 0.0% |
| **2026-08-09** | 19,952 | 5,976 | 30.0% | 11,091 | 55.6% | 2,885 | 14.5% |
| 2026-08-10 | 19,952 | 6,066 | 30.4% | 10,908 | 54.7% | 2,978 | 14.9% |
| 2026-08-12 | 19,952 | 5,253 | 26.3% | 12,157 | 60.9% | 2,542 | 12.7% |
| 2026-08-16 | 19,952 | 5,791 | 29.0% | 11,322 | 56.7% | 2,839 | 14.2% |
| 2026-08-24 | 19,952 | 6,061 | 30.4% | 10,991 | 55.1% | 2,900 | 14.5% |
| 2026-09-01 | 19,952 | 5,941 | 29.8% | 11,145 | 55.9% | 2,866 | 14.4% |

Every date 08-09 → 09-01 sits in a tight band (ok 26–30%, 429 55–61%, silent 13–15%). Zero
HTTP 429s exist anywhere in the bucket before 08-09; the only prior errors are ~1–3 HTTP 502/503
per day. Corroborated by S3 object size: mean batch file (100 records each) is **123.9 KiB on
08-08, 40.4 KiB on 08-09**, flat on either side.

The silent-empty mode stepped up at the same instant (1–2/day → 2,866/day). It is **not** stale
IDs.

## 2. Root cause: Tesco/Akamai, not us

Nothing in the repo lines up with 08-09:

- `tesco/tesco_api.py` unchanged since 2026-05-19; `tesco/graphql_query.txt` since 2026-02-12;
  `lambda/handler.py` since 2026-06-16. No commit at all between 2026-07-29 and 2026-08-11.
- Lambda `Environment.Variables` is `null` → `TOTAL_CHUNKS` = default **5** (`lambda/handler.py:15`),
  stable since June. 200 files/day = 5 chunks × 40 batches, unchanged.
- Tesco ID count = 19,952 since 2026-06-24; `raw/tesco/ids/` has no partition after 2026-06-23.

Decisive: on 2026-08-08 the scrape ran at ~14 req/s aggregate with **zero** 429s; on 2026-08-09
the same code at the same rate was 70% rejected.

### Live reproduction

Replaying `tesco_api.py`'s exact headers/payload/pacing (concurrency 5, `sleep(0.5)`) from a
residential IP:

```
429 hdrs: {'Retry-After': '1', 'X-RateLimit-Limit': '150', 'X-RateLimit-Remaining': '0'}
6.7 req/s (concurrency 5)  -> 33% rejected
```

Response headers show `x-queueit-connector: akamai` and `Server-Timing: ... ak_p` →
**Akamai Rate Controls**. The API key is fine (5/5 isolated requests OK at ~0.3 s).

Rate calibration (sequential, evenly paced, 45 requests each):

| rate | failures |
|---|---|
| 1.0 req/s | 0 / 45 |
| 2.0 req/s | 0 / 45 |
| 3.0 req/s | 1 / 45 (2%) |
| 6.7 req/s (concurrency 5) | 20 / 60 (33%) |

The limit is **rate/burst-sensitive, not count-sensitive**. Treat `X-RateLimit-Limit: 150` as
advertised metadata with an unspecified short window; the **measured sustainable knee is
~2.5 req/s**, and bursty concurrency trips it harder than even pacing at the same average.

### Current settings vs. that budget (`tesco/tesco_api.py`)

- `CONCURRENT_REQUESTS = 5` — line 25
- `DELAY_BETWEEN_BATCHES = 2` — line 26
- `await asyncio.sleep(0.5)` inside the semaphore — line 123
- `asyncio.Semaphore(CONCURRENT_REQUESTS)` — line 143
- `batch_size = 100` — line 149
- bare `aiohttp.ClientSession()` — line 145: **no `TCPConnector` limit, no `ClientTimeout`**
  (contrast `supervalu/supervalu_ids.py:102-103`, which sets both)
- `TOTAL_CHUNKS` = 5, all Batch array tasks submitted simultaneously — `lambda/handler.py:15,36-49,63`

Measured 2026-09-01 (files land 09:01:35 → 09:26:21, 1,486 s): **~13.4 req/s aggregate,
~2.7 req/s per container** — ~5× the sustainable aggregate rate.

**No 429 handling exists.** `fetch_product` (lines 119-137): no retry, no backoff, ignores
`Retry-After`. A 429 is a permanent per-day failure. `tenacity` is already a dependency (used in
`supervalu/supervalu_ids.py:38`, `dunnes/dunnes_ids.py:22`).

**Undetermined:** whether the budget is per-source-IP or per-API-key. `assignPublicIp: ENABLED` on
Fargate gives each of the 5 tasks its own public IP, so per-container rate (2.7 req/s) sits right
at the measured knee — yet production fails 70%. Either the bucket is shared per-API-key across
tasks, or Akamai rates AWS datacenter IPs more harshly than residential. Not resolvable from one
vantage point. The recommended fixes work either way.

## 3. The silent-empty mode — a correctness bug, also a 429

`tesco/tesco_api.py:128-134`:

```python
if response.status == 200:
    data = await response.json()
    return {"tpnc": tpnc, "data": data[0].get("data", {}).get("product"), "error": None}
```

Tesco returns some rate-limit rejections **at the GraphQL layer with HTTP 200**. Captured live:

```
{'errors': [{'message': 'Too many requests', 'extensions': {'http': {'status': 429}}}], ...}
```

No `data` key → `.get("data", {})` → `{}` → `.get("product")` → `None`, and `error` stays `None`.
Result: `{tpnc, data: null, error: null}`.

It stayed invisible because lines 161-162 count successes by `r["data"]` and failures by
`r["error"]` — these rows are **neither**, so the job's "Success: X, Failed: Y" log has never
accounted for 14.4% of the catalogue.

Independent of rate limiting: *any* body-level GraphQL error is silently recorded as a successful
empty product.

Not the same tpncs each day: across 08-09/08-16/08-24/09-01, 11,398 tpncs were never silent,
6,233 silent once, 1,797 twice, 433 three times, only 91 all four.

## 4. Impact: rotating failures, ~33% resists union-backfill

Pairwise Jaccard of successful-tpnc sets across 08-09 / 08-16 / 08-24 / 09-01: **0.279–0.293**
(intersections 2,617–2,674) — rotating, not fixed. But not independent-random: intersections run
~48% above what independent 30% sampling predicts, so there is per-product bias.

| times OK in 4 dates | tpncs |
|---|---|
| 0 | **6,620 (33.2%)** |
| 1 | 6,945 |
| 2 | 3,710 |
| 3 | 1,304 |
| 4 | 1,373 |

**Union over 4 dates = 13,332 / 19,952 = 66.8%** (independence would predict ~75.7%). Of the 6,620
never-recovered, 3,291 were hard-429 on all four attempts.

### Downstream corruption

- **`dbt/snapshots/scd_product_prices.sql`** (`strategy='check'` on `price`/`was_price`/`unit_price`):
  a row absent from `int_tesco` is not compared, so no version is written. Because a *different*
  ~70% is missing each day, Tesco price history since 2026-08-09 has gaps **and wrong change-dates**
  — a change is stamped with the day the product got through, not the day it changed. Not
  repairable by backfilling scrapes alone; may warrant rebuilding the snapshot from backfilled raw
  partitions.
- **`int_all_supermarket_products`** writes a different ~30% of Tesco titles to
  `s3://.../processed/` each run → the embedding corpus keyed off it is unstable run-to-run.

### Checkpoint poisons retries

`tesco/tesco_api.py:163` extends `processed_ids` with *every* result regardless of outcome, so the
Batch retry (`attempts: 2`) resuming via `load_checkpoint` (lines 183-186) permanently skips every
tpnc that 429'd.

## 5. Recommended fixes, in order

1. **Honour `Retry-After` on 429** — `tesco/tesco_api.py:119-137`. Server sends `Retry-After: 1`.
   Retry 5–8 times, exponential backoff + jitter starting at the `Retry-After` value. Self-regulates
   regardless of per-IP vs per-key. `tenacity` already a dependency.
2. **Detect body-level rejections** — lines 129-134. Check for `errors` in `data[0]` and for a
   missing `data` key; classify as an error (`GraphQL 429`) and retry on the same path. Fix the
   counters at 161-162 so "neither success nor failure" is impossible.
3. **Pace to a global budget.** Aggregate across all chunks ≲ 2.0 req/s. Minimum:
   `CONCURRENT_REQUESTS` 5 → **2** (line 25), in-semaphore `asyncio.sleep(0.5)` → **2.0**
   (line 123) → ~1 req/s per container, ~2 req/s across 5 chunks. Better: replace semaphore +
   fixed sleep with a token-bucket pacer (even pacing survived 3 req/s at 2% loss where
   concurrency-5 bursts failed 33% at 6.7 req/s).
4. **Raise the Batch timeout — mandatory with (3).** A compliant full pass is 19,952 / 2.0 ≈
   **166 min**, but `attemptDurationSeconds` = **7,200** (120 min). Raise to **≥ 12,000 s**.
5. **Stop the checkpoint poisoning retries** — line 163: extend `processed_ids` only with tpncs
   that produced data or an unrecoverable error.
6. **Backfill** 2026-08-09 → present at the compliant rate. Note `scd_product_prices` change-dates
   cannot be reconstructed and may warrant a snapshot rebuild from backfilled raw partitions.
7. **Alerting.** Fail the job if 429-rate or silent-rate exceeds a few percent. Zero-cost canary:
   per-file size (123.9 KiB → 40.4 KiB).
8. **Speculative, only if 1–4 aren't enough:** if the budget is per-IP, raising `TOTAL_CHUNKS`
   (each Fargate task already gets its own public IP) raises throughput. If per-API-key, it makes
   things worse. Determine which first.

## 6. Open questions

- **Per-IP vs per-API-key budget** — undetermined (see §2).
- Which GraphQL error each historical silent row carried — unrecoverable; `tesco_api.py:132`
  discards the response body, only `null` was persisted. §3's classification rests on live
  reproduction, not archived data.
- Lambda last modified 2026-08-25 with no corresponding commit — after the transition, not causal,
  unexplained.

---

*Investigation: 2026-09-02, all 103 Tesco date partitions swept + live reproduction from a
residential IP.*
