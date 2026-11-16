"""Incremental pair scoring: a cross-encoder scores candidate product pairs once, forever.

The sibling of `pipeline.run_embed` for pairs. dbt (`int_match_candidates`) proposes candidate pairs
and writes them as Parquet; this module scores the ones not scored yet and appends the scores to
`scores/<scorer_id>/part-*.parquet`; dbt (`stg_match_scores`) reads them back. A score is keyed by
`pair_key`, the hash of the two texts the model sees, so an unchanged pair is never rescored and a
changed title scores only its own pairs. Parts are append-only, like the embedding tables.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Protocol

import polars as pl

from ml_common.keys import content_key, stable_hash
from ml_common.storage import Storage

logger = logging.getLogger(__name__)

OK = "ok"
ERROR = "error"
SCORES_PREFIX = "scores"
CANDIDATES_KEY = "candidates.parquet"
_PAIR_COLUMNS = ["pair_key", "text_a", "text_b"]
# Fields that change a score; name and batch size are operational.
_HASHED = ("model_id", "revision", "max_length")


def pair_key(text_a: str, text_b: str) -> str:
    """Hash of exactly what the model sees. dbt computes the same: sha256(text_a || chr(10) || text_b)."""
    return content_key(f"{text_a}\n{text_b}")


@dataclass(frozen=True)
class PairScorerSpec:
    """A cross-encoder pinned to a commit. `scorer_id` names its score table."""

    name: str
    model_id: str
    revision: str
    max_length: int = 128
    batch_size: int = 64

    @property
    def scorer_id(self) -> str:
        fields = asdict(self)
        return stable_hash({k: fields[k] for k in _HASHED})

    @property
    def table_prefix(self) -> str:
        return f"{SCORES_PREFIX}/{self.scorer_id}"


REGISTRY: dict[str, PairScorerSpec] = {
    s.name: s
    for s in (
        PairScorerSpec(
            name="bge-reranker-v2-m3",
            model_id="BAAI/bge-reranker-v2-m3",
            revision="953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e",
        ),
    )
}


def get_scorer_spec(name: str) -> PairScorerSpec:
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown scorer {name!r}; known: {sorted(REGISTRY)}") from None


@dataclass(frozen=True)
class ScoreResult:
    score: float | None
    error: str | None = None


class PairScorer(Protocol):
    def score(self, pairs: list[tuple[str, str]]) -> list[ScoreResult]:
        """One result per pair, in order. A bad pair yields an error result, never a skip."""
        ...


class CrossEncoderScorer:
    """Scores pairs with a sentence-transformers CrossEncoder (sigmoid output, 0 to 1)."""

    def __init__(self, spec: PairScorerSpec, device: str | None = None):
        self.spec = spec
        self.device = device
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            from ml_common.embedders import pick_device

            self.device = self.device or pick_device()
            logger.info(
                "Loading %s@%s on %s", self.spec.model_id, self.spec.revision[:8], self.device
            )
            self._model = CrossEncoder(
                self.spec.model_id,
                revision=self.spec.revision,
                device=self.device,
                max_length=self.spec.max_length,
            )
        return self._model

    def score(self, pairs: list[tuple[str, str]]) -> list[ScoreResult]:
        import numpy as np

        scores = self.model.predict(pairs, batch_size=self.spec.batch_size, show_progress_bar=False)
        return [
            ScoreResult(float(s)) if np.isfinite(s) else ScoreResult(None, "non-finite score")
            for s in scores
        ]


def read_scored_keys(storage: Storage, spec: PairScorerSpec) -> pl.DataFrame:
    """Pair keys with a successful score; error rows are not done, so they are retried."""
    empty = pl.DataFrame(schema={"pair_key": pl.String})
    parts = [
        storage.read_parquet(k, columns=["pair_key", "status"]).filter(pl.col("status") == OK)
        for k in storage.list(spec.table_prefix)
        if k.endswith(".parquet")
    ]
    return pl.concat([empty, *[p.select("pair_key") for p in parts]])


def pending_pairs(candidates: pl.DataFrame, done: pl.DataFrame) -> pl.DataFrame:
    """Distinct (pair_key, text_a, text_b) of the candidates with no successful score yet."""
    keyed = (
        candidates.select("text_a", "text_b")
        .unique()
        .with_columns(
            pl.struct("text_a", "text_b")
            .map_elements(lambda r: pair_key(r["text_a"], r["text_b"]), return_dtype=pl.String)
            .alias("pair_key")
        )
    )
    return keyed.select(_PAIR_COLUMNS).join(done, on="pair_key", how="anti")


@dataclass(frozen=True)
class ScoreSummary:
    pending: int
    scored: int
    failed: int


def run_score(
    spec: PairScorerSpec,
    candidates: pl.DataFrame,
    storage: Storage,
    scorer: PairScorer,
    *,
    limit: int | None = None,
    chunk_rows: int = 2048,
) -> ScoreSummary:
    """Score candidate pairs missing from the spec's table; one part file per chunk."""
    todo = pending_pairs(candidates, read_scored_keys(storage, spec))
    total = len(todo)
    todo = todo.head(limit) if limit is not None else todo
    logger.info("%s: %d pairs pending", spec.name, total)
    scored = failed = 0
    for start in range(0, len(todo), chunk_rows):
        rows = todo.slice(start, chunk_rows)
        results = scorer.score(list(zip(rows["text_a"], rows["text_b"], strict=True)))
        part = rows.with_columns(
            pl.Series("score", [r.score for r in results], dtype=pl.Float32),
            pl.Series("status", [ERROR if r.error else OK for r in results], dtype=pl.String),
            pl.Series("error", [r.error for r in results], dtype=pl.String),
            pl.lit(spec.scorer_id).alias("scorer_id"),
            pl.lit(datetime.now(UTC)).alias("scored_at"),
        )
        _write_manifest(storage, spec)
        storage.append_parquet(part, spec.table_prefix)
        bad = sum(r.error is not None for r in results)
        scored, failed = scored + len(results) - bad, failed + bad
        logger.info("%s: %d/%d done (%d failed)", spec.name, scored + failed, len(todo), failed)
    return ScoreSummary(pending=total, scored=scored, failed=failed)


def _write_manifest(storage: Storage, spec: PairScorerSpec) -> None:
    import json

    key = f"{spec.table_prefix}/manifest.json"
    if not storage.exists(key):
        body = {"spec": asdict(spec) | {"scorer_id": spec.scorer_id}}
        storage.write_bytes(key, json.dumps(body, indent=2).encode())
