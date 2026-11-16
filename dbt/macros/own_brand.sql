{#- Own-brand flag for the retailers whose payload has none (Dunnes and SuperValu expose it raw).
    A row in seeds/own_brand_overrides (supermarket, normalised brand) always wins; otherwise:

    Tesco - tesco_is_own_brand: the brand is Tesco's own name ("tesco", "tesco finest", ...) or F&F, or
      the brand is a Tesco-exclusive label that does not say "Tesco" but whose products name Tesco as
      returns/manufacturer address (stg_tesco.has_tesco_address): at least half of the brand's
      products in this run carry it, over at least 3 products so one-off imports do not count.
      brand_address_share and brand_address_n are window aggregates over the retailer's rows.
    Aldi - aldi_is_own_brand: Aldi sells almost only own labels, so every brand is own unless the seed
      lists it as third party (is_own_brand = false); a product with no brand is NULL (unknown). -#}
{% macro tesco_is_own_brand(brand_norm, brand_address_share, brand_address_n, override) %}
coalesce(
    {{ override }},
    regexp_matches({{ brand_norm }}, '^(tesco|fandf)( |$)')
    OR coalesce({{ brand_address_share }} >= 0.5 AND {{ brand_address_n }} >= 3, false)
)
{% endmacro %}

{% macro aldi_is_own_brand(brand_norm, override) %}
CASE WHEN {{ brand_norm }} IS NULL OR {{ brand_norm }} = '' THEN NULL ELSE coalesce({{ override }}, true) END
{% endmacro %}
