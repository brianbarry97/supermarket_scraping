-- An alias must resolve in one step: a canonical_key that is itself an alias_key would leave brand_key
-- pointing at another alias. Fails for every such row.
SELECT a.alias_key, a.canonical_key
FROM {{ ref('brand_aliases') }} AS a
INNER JOIN {{ ref('brand_aliases') }} AS b ON b.alias_key = a.canonical_key
