# A6 — Health & Wellness — rationale & escalations

## Summary

31 current leaves, 1,029 products.

- **14 leaves `map`** (305 products) — all of Vitamins & Supplements (7 leaves, 144), Sports
  Nutrition's three real product types (Protein Bars & Energy Gels, Protein Drinks, Protein
  Powder — 107), plus four non-H&W buckets that land coherently in one existing leaf
  (Nut Butters & Spreads → Peanut Butter; Oils → Cooking & Vegetable Oil; Sugar Alternatives
  → Sweeteners; Dried Fruit → Snacking Nuts & Dried Fruit).
- **17 leaves `dissolve`** (724 products) — every "Free From" leaf, every remaining "Benefit
  Foods" leaf, `Sports Nutrition > Sports Nutrition`, and two of the three
  `Nuts, Seeds & Dried Fruit` leaves.

## What survives in Health & Wellness

Only genuine, non-duplicated H&W product types, all under two aisles:

- **Sports Nutrition** — `Protein Bars & Energy Gels`, `Protein Drinks`, `Protein Powder`.
  Protein powder / bars / gels are a real distinct product type (owner declined an
  `is_protein` flag, so these stay as leaves). `Protein Powder`'s description is broadened to
  also hold creatine, pre-workout and electrolyte powders — they sell in the same range and
  have no other home in the frozen taxonomy.
- **Vitamins & Supplements** — all 7 leaves kept 1:1 (`Adult Multivitamins`, `Children &
  Teens`, `Cod Liver Oils`, `Energy & Immunity`, `General Health Supplements`,
  `Jointcare & Bone Health`, `Womens Health`). Medicinal supplements, clearly H&W, not found
  in any other department. Age is the identity for `Children & Teens` (same principle as baby
  food), so it is kept, not dissolved into the adult leaves.

No "Free From", "Benefit Foods", "Diet & Nutrition" or "Nuts, Seeds & Dried Fruit" survivor —
per the owner's settled decision these are attribute / marketing dumps and dissolve fully. The
dietary attributes are preserved on `is_gluten_free` / `is_dairy_free` / `is_organic` /
`is_vegan` / `is_sugar_free`, already backfilled to full coverage in `int_supervalu`.

## Deviation from the owner brief

**`Sports Nutrition > Sports Nutrition` is dissolved, not kept.** The owner keep-list names it,
but the justification in that line only covers bars/gels/powder, and it is a 6-item same-name
catch-all that fails the dissolve test outright. Destinations: acti snack keto granola ×2 →
`Food Cupboard > Breakfast Cereals > Muesli & Granola`; femfuelz super-greens powder, kinetica
collagen shots, kinetica zinc-mag tablets → `Health & Wellness > Vitamins & Supplements >
General Health Supplements`; femfuelz shaker → non-food equipment (no grocery leaf).

## Non-obvious `map` calls

- **Nut Butters & Spreads → `Food Cupboard > Jams, Honey & Spreads > Peanut Butter`.** ~20 of
  31 are literally peanut butter; almond/cashew butter and tahini (7) fold in because there is
  no nut-butter leaf; 2 Mor Taste berry preserves are the only real misfits (→ Jams &
  Preserves in the later pass). Mapped rather than dissolved to keep 29 products out of the
  orphan set. **See gap below — recommend renaming the target leaf.**
- **Sugar Alternatives → `Food Cupboard > Sugar > Sweeteners`.** Confirmed against the frozen
  leaf's own description, which explicitly lists "alternative sweeteners such as agave and
  coconut sugar".
- **Oils → `Food Cupboard > Oils > Cooking & Vegetable Oil`.** Only 2 products, both Biona
  organic coconut oil. `Food Cupboard > Oils > Cooking Fats` ("solid cooking fats") is an
  equally valid target; picked the oil leaf because shoppers search "coconut oil".
- **Dried Fruit → `Snacking Nuts & Dried Fruit`.** Clean — dried mango/apricot/fig/cranberry/
  date plus True Dates fruit-snack pouches; target leaf already covers "trail mix and
  dried-fruit snacks".

## Non-obvious `dissolve` calls

- **Gluten Free Breakfast Cereals (35)** — all breakfast cereal, but spans three frozen leaves
  (Cereals / Muesli & Granola / Porridge & Oats), so it cannot `map` to one `taxonomy_3`.
- **Nuts & Seeds (35)** and **Dried Grains & Pulses (13)** — each is a genuine even split:
  snacking nuts vs baking nuts/seeds for the former; dried pulses (→ Beans & Pulses) vs grains
  like couscous/quinoa/barley (→ Rice & Grains) for the latter. The owner's single suggested
  target (Beans & Pulses) would misfile roughly half of each.
- **Wheat Free (9)** — 9 Nairns products split ~5 sweet oat biscuits / ~4 oatcakes (crackers).
- **Benefit Foods > Drinks (83)** — the single largest dissolve; ~55 are herbal/green tea bags
  → `Food Cupboard > Tea > Green, Fruit & Herbal Tea`, the rest scatter across kombucha,
  vinegar, juice, flavoured water and shots.

## Cross-department collisions (for the consolidation pass to resolve)

- **Functional / wellness drinks — A5 already flagged A6 twice.** A5's `map.tsv` routes
  `Drinks > Health` and `Drinks > Smoothies` with the note "cross-dept Health & Wellness (A6)".
  The split is by format and is consistent, not a conflict:
  - A5 takes RTD functional drinks, pressed juices and ginger/turmeric/greens **shots** into
    `Drinks > Juice > *` and `Drinks > Water > Flavoured`.
  - A6 routes its Benefit Foods > Drinks **effervescent drink-mix tablets/powders** (Vit Hit,
    Berocca-style, Phizz) into `Health & Wellness > Vitamins & Supplements >
    General Health Supplements`, and matcha/tea into `Food Cupboard > Tea`.
  - Kombucha / water kefir: A6 sends these to `Drinks > Soft Drinks > Kombucha & Fermented
    Drinks`, which **agrees** with A5's target for the same products.
- **Cereal bars / oat bars / flapjacks / energy balls** (large share of Free From > Snacking,
  131) land in `Food Cupboard > Breakfast Cereals > Cereal Bars` (A4). Protein bars
  specifically stay in `Health & Wellness > Sports Nutrition > Protein Bars & Energy Gels` — the
  later per-item pass needs a rule for "protein flapjack" type products that could go either
  way; recommend: branded sports-nutrition protein bars → H&W, everything else → Cereal Bars.
- **Plant milk / milk & cream alternatives** — Free From > Dairy Free (73) dissolves mostly
  into `Milk, Yogurt, Butter & Eggs > Milk & Yogurt Alternatives > Milk & Cream Alternatives`
  (A2). Includes ambient/long-life cartons; A2's leaf will need to hold both chilled and
  ambient.
- **Tofu / tempeh** from both Benefit Foods > Ready Meals and > Canned Veg → `Chilled Food >
  Meat Alternatives` (A2), though the SuperValu products are ambient-packed.
- **GF pasta** → `Food Cupboard > Rice, Pasta & Noodles > Pasta` (A4).
- **Superfood / greens / protein powders** from Benefit Foods > Powders, Seeds & Toppers split
  between `Health & Wellness > Sports Nutrition > Protein Powder` (hemp/whey protein) and
  `Health & Wellness > Vitamins & Supplements > General Health Supplements` (spirulina, maca,
  wheatgrass, matcha, psyllium) — both are A6 leaves, no external collision, but the per-item
  pass needs the distinction.

## Taxonomy gaps — product types with NO clean home in the frozen 557-leaf taxonomy

1. **Rice cakes / corn cakes (~40+ products, mostly from Free From > Gluten Free Biscuits &
   Rice Cakes).** Nearest home is `Food Cupboard > Biscuits > Crackers & Crispbreads`, which is
   a poor fit for the chocolate-coated / yogurt-coated snacking rice cakes. Recommend a
   `Food Cupboard > Crisps, Snacks, Nuts & Popcorn > Rice & Corn Cakes` leaf, or widening
   `Crackers & Crispbreads`.
2. **Nut butters that aren't peanut butter (almond / cashew / mixed nut butter, tahini —
   ~10 products).** `Food Cupboard > Jams, Honey & Spreads > Peanut Butter` is scoped in its
   description to "smooth and crunchy peanut butter". **Recommend renaming that leaf to
   "Nut Butters & Tahini"** (matches the owner's stated rename intent) so the mapped Nut
   Butters & Spreads bucket fits cleanly.
3. **Ambient fermented vegetables (kimchi, sauerkraut, tinned jackfruit, tempeh) — ~10
   products across Benefit Foods > Canned Veg and > Ready Meals.** No fermented-foods leaf in
   any department; currently forced into `Tinned Vegetables` / `Meat Alternatives`.
4. **Meal-replacement drinks (Huel, YFood, Complan) — ~10 products.** Folded into
   `Health & Wellness > Sports Nutrition > Protein Drinks`; not strictly protein/sports.
   Consider a `Meal Replacement` leaf if volume grows.
5. **Superfood / greens powders (spirulina, maca, wheatgrass, chlorella, barley grass) and
   nutritional yeast — ~8 products.** Folded into `Vitamins & Supplements > General Health
   Supplements`; a `Superfood Powders` leaf would be cleaner.
6. **Sports supplements that aren't protein (creatine, pre-workout, electrolyte tablets/
   powders) — ~8 products.** Currently folded into `Sports Nutrition > Protein Powder` via a
   broadened description. A rename to "Protein & Sports Powders" would be more honest but the
   owner named the leaf "Protein Powder".
7. **Coffee syrups (Slims, Skinny flavour syrups) — ~4 products.** No home; parked in
   `Food Cupboard > Desserts & Sundries > Dessert Sauces & Toppings`.
8. **Coconut milk (culinary tinned) — a few products.** Nearest is `Food Cupboard > Asian >
   Cooking Sauces & Ingredients`; no dedicated leaf.

## New flags recommended

- None strictly required for this department — `is_gluten_free`, `is_dairy_free`, `is_vegan`,
  `is_organic`, `is_sugar_free` already cover the dissolved dietary buckets at full coverage.
- Optional: an `is_protein` / `is_sports_nutrition` flag would let the per-item pass keep
  "protein flapjack" type products discoverable in both `Cereal Bars` and Sports Nutrition
  without duplicating leaves. Recommend, don't act.
