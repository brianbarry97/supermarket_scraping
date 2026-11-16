{{ config(materialized='view') }}
{#- Cross-encoder scores of candidate pairs, from the ml_common store
    ({matching_prefix}/scores/<match_scorer_id>/part-*.parquet, appended by ml_common.cli.score).
    Parts are append-only; a pair_key (hash of the two texts the model saw) can in principle be
    scored twice, so the newest successful score wins. -#}
SELECT
    pair_key::VARCHAR AS pair_key,
    score::DOUBLE AS score,
    scored_at::TIMESTAMP AS scored_at
FROM read_parquet(
    '{{ var("matching_prefix") }}/scores/{{ var("match_scorer_id") }}/part-*.parquet',
    union_by_name = true
)
WHERE status = 'ok'
QUALIFY row_number() OVER (PARTITION BY pair_key ORDER BY scored_at DESC) = 1
