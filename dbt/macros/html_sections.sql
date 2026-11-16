{#- Dunnes embeds ingredients / allergy / lifestyle info in the description HTML as
    "<b>Heading</b><br/>body<br/><br/>". -#}
{% macro html_section(html, heading) %}
regexp_extract({{ html }}, '<b>{{ heading }}</b><br/>(.*?)(?:<br/><br/>|$)', 1)
{% endmacro %}


{% macro html_section_all(html, heading) %}
regexp_extract_all({{ html }}, '<b>{{ heading }}</b><br/>(.*?)(?:<br/><br/>|$)', 1)
{% endmacro %}


{#- Drops a leading "Ingredients" label from ingredient text: "INGREDIENTS:", "Ingredients :",
    "<b>Ingredients:</b>", non-breaking spaces, multilingual "INGREDIENTS/СЪСТАВКИ/...:" and a bare
    uppercase "INGREDIENTS Aqua, ...". A label-only value becomes NULL. Repeated labels ("<b>INGREDIENTS:</b> <b>INGREDIENTS:</b> x", seen on Tesco) all go. Only a *leading* label goes:
    "Ingredients per capsule ..." and a mid-text "ingredients" stay. Only tags that wrap the label are
    removed (not a free "<5%" in the text). Apply per list element when the source is a list. -#}
{% macro strip_ingredients_label(col) %}
NULLIF(
    regexp_replace(
        regexp_replace(
            regexp_replace(
                {{ col }},
                '(?i)^(?:(?:<[a-z/][^>]*>|[\s\x{00A0}])*ingredients?(?:(?:<[a-z/][^>]*>|[\s\x{00A0}])*/[^:/\s<]+)*(?:<[a-z/][^>]*>|[\s\x{00A0}])*(?::(?:<[a-z/][^>]*>|[\s\x{00A0}])*|$))+',
                ''),
            '^(?:<[a-z/][^>]*>|[\s\x{00A0}])*INGREDIENTS(?:/[^:/\s<]+)*(?:<[a-z/][^>]*>|[\s\x{00A0}])+',
            ''),
        '^[\s\x{00A0}]+|[\s\x{00A0}]+$', '', 'g'),
    ''
)
{% endmacro %}


{#- Ingredients section HTML -> single clean string; NULL if empty. -#}
{% macro html_ingredients_text(section) %}
NULLIF(
    trim(
        regexp_replace(
            regexp_replace(
                {{ strip_ingredients_label(
                    "regexp_replace(regexp_replace(" ~ section ~ ", '<br/>', ', ', 'g'), '<[^>]*>', '', 'g')"
                ) }},
                '\s+', ' ', 'g'),
            '([a-z])([A-Z])', '\1, \2', 'g')
    ),
    ''
)
{% endmacro %}
