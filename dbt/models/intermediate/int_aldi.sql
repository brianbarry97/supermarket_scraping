WITH stg AS (
    SELECT
        *,
        COALESCE(selling_size, price_comparison_display, title) AS size_text
    FROM {{ ref('stg_aldi') }}
    WHERE is_product_available IS TRUE
),

-- Aldi has no structured pack size, so quantity and unit are parsed from free text.
parsed AS (
    SELECT
        *,
        TRY_CAST(REGEXP_EXTRACT(size_text, '(\d+\.?\d*)') AS DOUBLE) AS selling_qty,
        LOWER(REGEXP_EXTRACT(size_text, '(\d+\.?\d*)\s*([a-zA-Z]+)', 2)) AS unit_raw
    FROM stg
),

normalised AS (
    SELECT
        *,
        {{ normalize_text('title') }} AS title_norm,
        {{ normalize_text('brand') }} AS brand_norm,
        {{ unit_qty_normalised('unit_raw', 'selling_qty', 'title_norm', count_units=['each', 'pack', 'pk', 'sheet', 'sheets', 'slices', 'rolls', 'pair', 'pairs']) }} AS unit_qty_normalised,
        {{ unit_normalised('unit_raw') }} AS unit_normalised
    FROM parsed
),

-- seed row for this retailer and brand (seeds/own_brand_overrides) overrides the own-brand rule; joined in
-- its own CTE so the seed's supermarket/brand columns cannot clash with the model's
overridden AS (
    SELECT normalised.*, brand_override.is_own_brand AS override_own_brand
    FROM normalised
    LEFT JOIN {{ ref('own_brand_overrides') }} AS brand_override
        ON brand_override.supermarket = 'aldi' AND brand_override.brand = normalised.brand_norm
)

SELECT
    id,
    supermarket,
    title_norm AS title,
    {{ clean_title('title') }} AS title_cleaned,
    brand_norm AS brand,
    {{ aldi_is_own_brand('brand_norm', 'override_own_brand') }}::BOOLEAN AS is_own_brand,
    description AS item_description,
    {{ normalize_category('category_1') }} AS category_1,
    {{ normalize_category('category_2') }} AS category_2,
    CAST(NULL AS VARCHAR) AS category_3,
    CAST(NULL AS VARCHAR) AS category_4,
    is_sale AS is_discount,
    CAST(NULL AS BOOLEAN) AS is_promotion,
    {{ parse_price('price_display') }} AS price,
    {{ parse_price('was_price_display') }} AS was_price,
    selling_qty AS selling_size,
    unit_raw AS unit,
    unit_qty_normalised,
    unit_normalised,
    -- raw price.perUnit is a pack weight, not a euro amount, so there is no usable unit price
    CAST(NULL AS DOUBLE) AS unit_price,
    {{ price_per_unit_normalised('price', 'unit_qty_normalised', 'unit_normalised') }} AS price_per_unit_normalised,
    CAST(NULL AS VARCHAR) AS promotion_description,
    CAST(NULL AS VARCHAR) AS promotion_type,
    CAST(NULL AS DATE) AS promotion_start_date,
    CAST(NULL AS DATE) AS promotion_end_date,
    -- raw onSaleDate is a stock-availability date, not a discount start
    CAST(NULL AS DATE) AS discount_start_date,
    CAST(NULL AS DATE) AS discount_end_date,
    -- placeholders such as 'N/A', 'na' (incl. non-breaking-space variants) become NULL
    CASE
        WHEN ingredients IS NULL THEN NULL
        WHEN regexp_replace(upper(ingredients), '[^A-Z]', '', 'g') = 'NA' THEN NULL
        ELSE {{ strip_ingredients_label('ingredients') }}
    END AS ingredients,
    list_transform(
        list_filter(nutritional_claims, lambda claim: lower(claim.label) = 'contains'),
        lambda claim: claim.value
    ) AS contains_allergens,
    list_transform(
        list_filter(nutritional_claims, lambda claim: lower(claim.label) = 'may contain'),
        lambda claim: claim.value
    ) AS may_contain_allergens,
    CAST(NULL AS VARCHAR[]) AS dietary_flags,
    CAST(NULL AS BOOLEAN) AS is_vegan,
    CAST(NULL AS BOOLEAN) AS is_vegetarian,
    CAST(NULL AS BOOLEAN) AS is_gluten_free,
    CAST(NULL AS BOOLEAN) AS is_organic,
    CAST(NULL AS BOOLEAN) AS is_low_fat,
    CAST(NULL AS BOOLEAN) AS is_kosher,
    CAST(NULL AS BOOLEAN) AS is_halal,
    CAST(NULL AS BOOLEAN) AS is_dairy_free,
    CAST(NULL AS BOOLEAN) AS is_sugar_free,
    CAST(NULL AS BOOLEAN) AS has_no_added_sugar,
    -- Scene7 template URL: fix the width and drop the optional slug segment
    replace(replace(image_url_raw, '{width}', '600'), '{slug}', '') AS image_url,
    is_product_available,
    scraped_date
FROM overridden
