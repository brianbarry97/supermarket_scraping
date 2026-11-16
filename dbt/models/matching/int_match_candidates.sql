{{ config(
    materialized='external',
    location=var('matching_prefix') ~ '/candidates.parquet'
) }}
{#- Candidate product pairs across retailers, for the cross-encoder to score (ml_common.cli.score).
    Written as Parquet because the scorer is Python; stg_match_scores reads the scores back.
    A pair is a candidate only when its size agrees EXACTLY (same unit_normalised and the same
    unit_qty_normalised to 3 decimals, i.e. to the gram/ml) and one of:
      same_brand  both products have the same brand (excluding the 'unbranded' placeholder);
      own_brand   the brands differ and at least one product is a retailer own-brand line
                  (is_own_brand), e.g. a Dunnes Stores ketchup and a branded Chef ketchup.
    Each product keeps its best candidates per other retailer and kind by cosine similarity of the
    stored title embeddings (emb_gemma2_text), above a floor below which matches were measured to be
    almost all wrong. Only embeddings of the CURRENT title_cleaned are used (content_key =
    sha256(title_cleaned)); a product whose title changed since it was embedded is skipped until
    ml_common re-embeds it. Pairs are stored once, supermarket_a < supermarket_b.
    match_text is the title without its brand prefix (and, for own-brand lines, the retailer
    sub-line prefix listed in var own_brand_lines, which the cross-encoder otherwise penalises): brand agreement is decided here, so the
    cross-encoder only has to judge product type and variant. -#}
{% set same_brand_top, own_brand_top = 5, 3 %}
{% set same_brand_floor, own_brand_floor = 0.75, 0.75 %}

WITH products AS (
    SELECT
        l.supermarket,
        l.id,
        l.brand,
        coalesce(l.is_own_brand, false) AS is_own_brand,
        l.unit_normalised,
        round(l.unit_qty_normalised, 3) AS unit_qty,
        e.embedding,
        {#- brand prefix, then (own-brand lines only) a retailer sub-line prefix such as 'simply better' -#}
        CASE
            WHEN coalesce(l.is_own_brand, false)
                THEN regexp_replace(
                    CASE WHEN starts_with(l.title_cleaned, l.brand || ' ')
                        THEN trim(substr(l.title_cleaned, length(l.brand) + 2)) ELSE l.title_cleaned END,
                    '^({{ var("own_brand_lines") | join("|") }}) ', ''
                )
            WHEN starts_with(l.title_cleaned, l.brand || ' ')
                THEN trim(substr(l.title_cleaned, length(l.brand) + 2))
            ELSE l.title_cleaned
        END AS match_text
    FROM {{ ref('fct_product_listings') }} AS l
    INNER JOIN {{ ref('emb_gemma2_text') }} AS e
        ON e.supermarket = l.supermarket AND e.id = l.id
    WHERE e.vector_index = 0
      AND e.content_key = sha256(l.title_cleaned)
      AND l.brand IS NOT NULL
      AND l.unit_normalised IS NOT NULL
      AND l.unit_qty_normalised IS NOT NULL
      AND l.title_cleaned <> ''
    QUALIFY row_number() OVER (PARTITION BY l.supermarket, l.id ORDER BY l.scraped_date DESC) = 1
),

pairs AS (
    SELECT
        a.supermarket AS supermarket_a,
        a.id AS id_a,
        b.supermarket AS supermarket_b,
        b.id AS id_b,
        CASE WHEN a.brand = b.brand THEN 'same_brand' ELSE 'own_brand' END AS pair_kind,
        array_cosine_similarity(a.embedding, b.embedding) AS cosine,
        a.unit_normalised,
        a.unit_qty,
        a.match_text AS text_a,
        b.match_text AS text_b
    FROM products AS a
    INNER JOIN products AS b
        ON a.supermarket < b.supermarket
        AND a.unit_normalised = b.unit_normalised
        AND a.unit_qty = b.unit_qty
    WHERE (a.brand = b.brand AND a.brand <> 'unbranded')
       OR (a.brand <> b.brand AND (a.is_own_brand OR b.is_own_brand))
)

SELECT
    *,
    sha256(text_a || chr(10) || text_b) AS pair_key
FROM pairs
WHERE cosine >= CASE pair_kind
        WHEN 'same_brand' THEN {{ same_brand_floor }} ELSE {{ own_brand_floor }} END
QUALIFY row_number() OVER (
            PARTITION BY supermarket_a, id_a, supermarket_b, pair_kind ORDER BY cosine DESC
        ) <= CASE pair_kind WHEN 'same_brand' THEN {{ same_brand_top }} ELSE {{ own_brand_top }} END
    OR row_number() OVER (
            PARTITION BY supermarket_b, id_b, supermarket_a, pair_kind ORDER BY cosine DESC
        ) <= CASE pair_kind WHEN 'same_brand' THEN {{ same_brand_top }} ELSE {{ own_brand_top }} END
