{#- Products matched across retailers, one row per (product, matched product), in both directions.
    A candidate pair (int_match_candidates: exact size agreement, brand rule) is accepted when its
    cross-encoder score reaches match_min_score. match_type:
      exact                 same brand, same size, score >= match_min_score. The same product.
      own_brand_equivalent  different brands, one of them a retailer own-brand line, same size,
                            score >= match_min_score on the brand-stripped titles. A substitute.
    match_rank orders a product's accepted matches within one other retailer and match_type (1 is
    best, by score then cosine). is_mutual: the pair is each other's rank 1 of the same type, so
    a consumer wanting at most one-to-one links filters match_rank = 1 AND is_mutual. -#}
WITH accepted AS (
    SELECT c.*, s.score
    FROM {{ ref('int_match_candidates') }} AS c
    INNER JOIN {{ ref('stg_match_scores') }} AS s USING (pair_key)
    WHERE s.score >= {{ var('match_min_score') }}
),

directed AS (
    SELECT
        supermarket_a AS supermarket, id_a AS id, supermarket_b AS match_supermarket, id_b AS match_id,
        pair_kind, score, cosine, unit_normalised, unit_qty
    FROM accepted
    UNION ALL
    SELECT
        supermarket_b, id_b, supermarket_a, id_a,
        pair_kind, score, cosine, unit_normalised, unit_qty
    FROM accepted
),

ranked AS (
    SELECT
        *,
        CASE pair_kind WHEN 'same_brand' THEN 'exact' ELSE 'own_brand_equivalent' END AS match_type,
        row_number() OVER (
            PARTITION BY supermarket, id, match_supermarket, pair_kind
            ORDER BY score DESC, cosine DESC, match_id
        ) AS match_rank
    FROM directed
)

SELECT
    r.supermarket,
    r.id,
    r.match_supermarket,
    r.match_id,
    r.match_type,
    r.match_rank,
    r.match_rank = 1 AND rev.match_rank = 1 AS is_mutual,
    r.score,
    r.cosine,
    r.unit_normalised,
    r.unit_qty AS unit_qty_normalised,
    l.title,
    l.brand,
    m.title AS match_title,
    m.brand AS match_brand
FROM ranked AS r
INNER JOIN ranked AS rev
    ON rev.supermarket = r.match_supermarket AND rev.id = r.match_id
    AND rev.match_supermarket = r.supermarket AND rev.match_id = r.id
    AND rev.pair_kind = r.pair_kind
INNER JOIN {{ ref('fct_product_listings') }} AS l
    ON l.supermarket = r.supermarket AND l.id = r.id
INNER JOIN {{ ref('fct_product_listings') }} AS m
    ON m.supermarket = r.match_supermarket AND m.id = r.match_id
