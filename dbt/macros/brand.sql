{#- Brand cleaning and the cross-retailer brand key.
    normalize_brand: normalize_text, then trim and collapse runs of whitespace (some retailers pad the brand
    with trailing spaces); an empty brand becomes NULL.
    with_brand_key: adds brand_key to a CTE that has brand_norm. brand_key is the brand with all spaces removed
    ("birds eye" and "birdseye" both give birdseye), then mapped through the reviewed seeds/brand_aliases
    (alias_key -> canonical_key, e.g. keoghscrisps -> keoghs). It is only used to decide whether two brands are the
    same; `brand` keeps each retailer's own spelling. -#}
{% macro normalize_brand(col) %}
NULLIF(trim(regexp_replace({{ normalize_text(col) }}, '\s+', ' ', 'g')), '')
{% endmacro %}

{% macro with_brand_key(rel) %}
SELECT
    {{ rel }}.*,
    coalesce(brand_alias.canonical_key, replace({{ rel }}.brand_norm, ' ', '')) AS brand_key
FROM {{ rel }}
LEFT JOIN {{ ref('brand_aliases') }} AS brand_alias
    ON brand_alias.alias_key = replace({{ rel }}.brand_norm, ' ', '')
{% endmacro %}
