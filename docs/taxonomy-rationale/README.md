# SuperValu taxonomy consolidation — Phase 2 output

The unified taxonomy lives in three dbt seeds:

| seed | rows | what it is |
|---|---|---|
| `dbt/seeds/supervalu_taxonomy.csv` | 567 leaves | the canonical 3-level product-type tree (`taxonomy_1/2/3` + `description`) |
| `dbt/seeds/supervalu_category_map.csv` | 687 rows | one row per current raw `category_1..4` path → `taxonomy_1/2/3` + `disposition` (`map` \| `dissolve`) + `note` |
| `dbt/seeds/supervalu_product_overrides.csv` | header only | per-product assignment for `dissolve` paths — filled by the Phase 3 LLM pass + Phase 4 human review |

Coverage (verified against the 2026-09-01 scrape, 14,940 live products / 683 distinct paths):
**12,690 products remap mechanically, 2,250 need per-product classification** (72 `dissolve` buckets).

The per-department rationale from the six design agents is in `A1_*.md` … `A6_*.md` here.

## How the taxonomy was built

Six agents redesigned the tree by department against one rule — *does the bucket name answer "what
is this product?", or does it describe a segment / tier / claim / attribute?* Only the first
survives. Sourcing splits (`Beef > Butcher` vs `Beef > Pre-pack`) were merged away; attribute dumps
(`Organic`, `Gluten Free`, `Free From`, `Benefit Foods`) and marketing tiers (`Luxury`, `Everyday`,
`Healthier`, `Premium Italian`) were dissolved; the duplicate `Deli Counter` department was folded
into `Chilled Food`. Non-food departments (Beauty, Household, Baby, Pets, Newsagent) got mechanical
depth-normalisation only.

Settled design decisions: no new attribute flags (minor characteristics — decaf, craft, protein,
breaded — are inferred from the title at search time); storage state stays a taxonomy axis (chilled
soup and tinned soup are separate leaves).

## Known issues carried into Phase 3/4

These came out of the agent escalations and the consolidation pass. The Phase 3 LLM pass and Phase 4
review should watch for them:

1. **World Foods cuisine scatter.** `Food Cupboard > {Asian, Japanese, Thai} > Cooking Sauces &
   Ingredients` are three near-identical leaves — soy sauce / coconut milk legitimately belong in
   all three. Kept because cuisine *is* how shoppers navigate world foods, but a shared "Asian
   staples" leaf is a defensible alternative if the shopping agent struggles.
2. **Breaded/coated proteins** split across `Meat & Poultry > Chicken & Poultry > Breaded & Coated
   Poultry`, `Fish & Seafood > Prepared Fish > Breaded Fish & Fishcakes`, and `Frozen Foods >
   Frozen Fish & Seafood > {Breaded, Battered, Fish Fingers}`. Fresh vs frozen is a real axis; the
   LLM pass must route consistently within each temperature zone.
3. **Meat alternatives** — RESOLVED. `Meat & Poultry` is now actual meat only; all *chilled*
   meat-free items (meat-free sausages/rashers/pudding, tofu, Quorn pieces, falafel) route to
   `Chilled Food > Meat Alternatives`. Frozen meat-free stays under `Frozen Foods > Frozen
   Vegetarian & Meat-Free` (fresh/frozen split is deliberate). `is_vegan`/`is_vegetarian` bridge
   the two zones at query time.
4. **Soup, pesto, olives, custard, dips, stuffing, garlic bread, pizza, sausage rolls** each have a
   chilled leaf and an ambient/frozen leaf. Intentional (state axis) — not a bug.
5. **Cheese residue** — RESOLVED. The flat `Cheese > Continental & Speciality Cheese` source
   bucket (44) was flipped from `map` to `dissolve` so its sheep/goat (manchego, ossau iraty →
   `Goats & Sheep Cheese`) and blue (gorgonzola, roquefort, cashel blue) members get routed
   per-item. No dedicated `Blue Cheese` leaf — blue stays under `Continental & Speciality Cheese`.
6. **`Prepared By Our Butcher`** (63, dissolve) is a genuine 3-way mix: raw marinated meat →
   `Meat & Poultry > Prepared Meats`, veg side dishes → `Chilled Food > Ready Meals > Side Dishes`,
   cooked items → `Chilled Food`. The LLM pass must split it, not bucket it.
7. **Small-bottle wine / fizzy multipacks / ice-cream "Luxury"** are large packaging/tier dissolve
   buckets (7+7 / 82 / 90) — pure per-item classification, no shortcut.
8. **Leaf renames applied in consolidation:** `Jams… > Peanut Butter` → `Nut Butters & Tahini`;
   `Biscuits > Crackers & Crispbreads` → `Crackers, Crispbreads & Rice Cakes`;
   `Condiments > Pickles & Beetroot` → `Pickles & Fermented Foods` (absorbs kimchi/sauerkraut).
   Ambient fermented veg now has a home; the Phase 3 pass still needs to route it there
   consistently (was a flagged gap).
