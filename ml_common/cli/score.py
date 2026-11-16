import argparse
import os

from ml_common.config import setup_logging
from ml_common.pairs import (
    CANDIDATES_KEY,
    REGISTRY,
    CrossEncoderScorer,
    get_scorer_spec,
    run_score,
)
from ml_common.storage import Storage


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Score candidate product pairs not yet scored.")
    parser.add_argument("--scorer", required=True, choices=sorted(REGISTRY))
    parser.add_argument(
        "--store",
        default=os.environ.get("MATCHING_STORE", "matching_store"),
        help="dbt var matching_prefix: holds candidates.parquet and scores/<scorer_id>/",
    )
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)

    logger = setup_logging("score")
    spec = get_scorer_spec(args.scorer)
    storage = Storage(args.store)
    summary = run_score(
        spec,
        storage.read_parquet(CANDIDATES_KEY, columns=["text_a", "text_b"]),
        storage,
        CrossEncoderScorer(spec),
        limit=args.limit,
        chunk_rows=int(os.environ.get("CHUNK_ROWS", "2048")),
    )
    logger.info("%s (scorer_id %s)", summary, spec.scorer_id)


if __name__ == "__main__":
    main()
