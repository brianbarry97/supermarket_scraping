# A5 — Frozen Foods, Drinks, Wine Beer & Spirits — rationale & escalations

Result: **107 leaves** (from 135 current). **125 map rows, 13 dissolve rows**, 138 total (one per current leaf path; includes 1 leaf present in the DB but absent from `full_taxonomy.txt` — White Wine > France - Rhone — and 2 leaves in `full_taxonomy.txt` absent from the DB — Red Wine > Eastern Europe, Red Wine > Other Red Wine).

## Wine (per project-owner instructions)

- **Dropped the redundant `Wine` c2 level.** `WBS > Wine > Red Wine > Spain` → `WBS > Red Wine > Spain`. Same for White Wine, Rosé, Champagne & Sparkling, Fortified & Dessert. taxonomy_1 stays `Wine, Beer & Spirits`.
- **Country = taxonomy_3** for Red and White wine (real sub-type for wine). `Usa` normalised to `USA`.
- **France sub-regions collapsed to one `France` leaf.** `France - Bordeaux/Burgundy/Loire/Rhone/Other/Vin De Pays` (6 red-side, 6 white-side) → `France`. Every sibling country leaf (`Spain`, `Chile`, …) is single-level, so region granularity was the odd one out. These are still coherent `map`s (all French red / all French white). *Escalation-lite:* if wine-region matters to the agent, Bordeaux / Burgundy / Rhône are defensible standalone leaves — easy to re-split later since the raw c4 is retained in the map.
- `Wine > Gifting Wine` (1) → **dissolve** (gift-pack bucket).
- `Wine > Port, Sherry, Fortified & Dessert > Other Fortified & Dessert Wines` (4) → **dissolve** — catch-all c4; contents are 3× Martini vermouth + Buckfast tonic wine. **Recommend a `Vermouth` leaf** if another department turns up more vermouth (see cross-dept).
- `Port` and `Sherry` c4s → kept, as `Fortified & Dessert Wine > Port` / `> Sherry` (redundant middle dropped).
- `Red/White Wine > Small Bottles` (7 + 7) → **dissolve** — packaging (18.75cl / 37.5cl), mixed countries, cannot mechanically remap.
- `Red Wine > Other Red Wine` (1) → **dissolve**.

## Wine, Beer & Spirits — other

- **`Craft Beer & Cider` dissolved as a marketing tier**: `> Ale/Lager/Stout` merged into `Beer > Ale/Lager/Stout`; `> Cider` into `Cider & Alcopops > Cider`. Likewise `Non Alcoholic > Non Alcoholic Craft World Beer` → `Non-Alcoholic Beer & Cider`. **Recommend an `is_craft` boolean flag** — "craft" is real shopper intent but has no clean definition and shouldn't be a category.
- **`Spirits & Liqueurs > Other Spirits` (74) → dissolve.** Genuine grab-bag: liqueurs (Cointreau, Kahlúa, Tia Maria, Campari, Aperol, Jägermeister…), tequila (Jose Cuervo, Olmeca, Sierra, Rooster Rojo…), pre-mixed bottled cocktails (Tails, Coppa, Le Coq), RTD spirit cans + hard seltzers (White Claw, Au Vodka, JD & Cola), schnapps. Two **new real leaves created** to catch the bulk: `Tequila`, `Liqueurs`. RTD cans / seltzers go to `Cider & Alcopops > Alcopops & RTDs`.
- `Alcopops` renamed `Alcopops & RTDs` (already holds premixed cans, RTD cocktails, seltzers).
- Kept `American / Irish / Scotch` whiskey as separate leaves (real sub-types), `Brandy` → `Brandy & Cognac`.
- `Non Alcoholic Spirits & Liquers` mapped whole but **contains cocktail/mixer syrups** (Master of Mixes, Jose Cuervo margarita mix) that are really mixers — flagged, small.

## Frozen Foods

Dissolves:
- **`Ice Cream & Desserts > Luxury` (86–90) → dissolve** (marketing tier). Splits across `Ice Cream Tubs & Blocks`, `Ice Cream Sticks, Cones & Lollies`, `Mochi & Ice Cream Bites`, new `Frozen Desserts & Gateaux`. Biggest single orphan set in this department.
- **`Ice Cream & Desserts > Health & Dietary Ice Cream` (22–23) → dissolve** (attribute dump: low-fat / dairy-free / vegan / high-protein). Dietary flags backfilled per brief; products land in `Ice Cream Tubs & Blocks` / `Sticks, Cones & Lollies` / new `Frozen Yogurt`.
- **`Ice Cream & Desserts > Snacking Ice Cream` (16) → MAP** to new `Mochi & Ice Cream Bites` (not dissolve). Titles show a real, coherent format cluster: Little Moons / other mochi, Magnum bon-bons, TruFru choc-coated frozen fruit. King Cone + ice-cream swirls are 2 minor strays.
- **`Frozen Pizza… > Speciality` (4–5) → dissolve** (marketing; stonebaked/woodfired pizzas → deep pan / thin & crispy).
- **`Frozen Pizza… > Snacking` (13) → MAP** to new `Mini & Snacking Pizza` (mini pizzas, pizza pockets, pizzinis, air-fryer pizza — coherent small-format).
- **`Frozen Pizza… > Breads` (8) → dissolve.** Mixed: garlic bread / baguettes / toasties (→ new `Garlic Bread` leaf) + frozen croissants & pains au chocolat + penny-loaf soda bread (→ Bakery, cross-dept).
- `Frozen Chips… > Other` (9) → **MAP** to new `Potato Shapes, Bites & Onion Rings` (coherent: potato smiles/bites/cubes, jacket potatoes, crispy slices, onion rings — the category name already promises "Onion Rings" but had no leaf).
- `Frozen Fish & Seafood > Other` (1, marinated salmon) → map to `Salmon, Prawns & Seafood` (that leaf already mixes salmon fillets/darnes with prawns; renamed from `Prawns & Seafood`).

Kept (brief-confirmed real product types): `Frozen Burgers & Sausages > {Burgers, Sausages}`; `Frozen Poultry > {Chicken Burgers, Chicken Fillets, Chicken Nuggets & Goujons, Takeaway Chicken}` (last renamed `Southern Fried & Takeaway Chicken`); pizza `Deep Pan` / `Thin & Crispy`.

Consolidations:
- `Frozen Vegetables`: `Frozen Steam & Microwave Vegetables` (packaging) merged into `Vegetables & Sweetcorn`; `Frozen Mixed Vegetables` → `Mixed Vegetables & Stir Fry`; `Peas & Beans` kept.
- `Frozen Vegetarian`: `Meals` (Quorn fillets/nuggets/pieces/burgers — mislabelled, not meals) + `Vegetable Pieces & Fillets` → `Meat-Free Fillets, Pieces & Nuggets`; `Burgers & Sausages` → `Meat-Free Burgers & Sausages`.
- `Frozen Pastry… > Pies` (jambons, mozzarella sticks, gyoza — no actual pies) → `Savoury Pastries & Snacks`.
- `Frozen Meals` (1–4 products) → kept as 2-level `Frozen Ready Meals`.

## Drinks

- `Juice` is 4-level (`Juice > Chill & Long Life | Freshly Squeezed > flavour`). **Format split dropped** — it's a shelf distinction, not identity. Flavour = taxonomy_3: `Apple / Orange / Cranberry / Coconut Water / Vegetable / Other Fruit Juice`. Small flavour leaves (`Prune Juice`, `Tropical & Mixed Fruit`) folded into `Other Fruit Juice`.
- `Smoothies` → `Juice > Smoothies` (includes ginger/turmeric/immunity shots — minor).
- **`Soft Drinks > Adult Drinks` (61) → dissolve** (marketing). Grab-bag: premium sparkling juice drinks / pressés (Shloer, Fentimans, Bottlegreen), kombucha & water kefir (~15), iced coffee (Starbucks, Jimmy's), gut sodas, matcha energy. **Three new leaves created** to catch it: `Adult Soft Drinks & Presses`, `Kombucha & Fermented Drinks`, `Iced Coffee`.
- **`Soft Drinks > Fizzy Drinks > Multipack` (82) → dissolve** — pure packaging bucket, all flavours mixed, cannot mechanically remap. Second-biggest orphan set.
- Fizzy bottle/can splits collapsed by flavour: `Cola`, `Orange`, `Lemonade & Lemon-Lime`.
- **Deviation from brief:** `Fizzy Drinks > Other Cans` + `Other Flavours` (21) → **MAP** to a kept leaf `Other & Mixed Fizzy Drinks` rather than dissolve. Contents (Cidona, Irn-Bru, ginger beer, rock shandy, cream soda, San Pellegrino) are a coherent "other-flavoured fizzy soft drink" product type and a shopping agent needs a home for Irn-Bru. Multipack orphans also land here.
- `Dilutes & Cordials` → 2-level `Squash & Cordials`. `Mixers`, `Kids Drinks`, `Iced Tea`, `Sports & Energy Drinks` kept (kids-drink format is identity, cf. Kids Yogurts in the brief).
- `Water > Other` (3, all Vita Coco) → `Juice > Coconut Water`. `Water > Still / Sparkling / Flavoured` kept.
- **`Drinks > Health` (3) → dissolve** (benefit claim; 3 Vit Hit drinks).

## Cross-department collisions (for the consolidation pass)

1. **Coconut water** — my `Drinks > Juice > Coconut Water` vs. water-aisle placement; also Vita Coco currently under `Drinks > Water > Other`. Resolved internally, but A6 (Health & Wellness) may also carry coconut water.
2. **Kombucha / water kefir / gut sodas / functional shots** — my new `Drinks > Soft Drinks > Kombucha & Fermented Drinks` and `Juice > Smoothies` (shots) overlap `Health & Wellness > Benefit Foods > Drinks` (A6, 81 products). Vit Hit appears in my `Drinks > Health`, `Drinks > Kids`, `Drinks > Smoothies` **and** likely A6.
3. **Protein / iced-coffee drinks** — Jimmy's protein iced coffee, Starbucks: my `Iced Coffee` vs `Health & Wellness > Sports Nutrition > Protein Drinks` (A6).
4. **Mixers vs Spirits** — `Drinks > Mixers` (tonic, soda, ginger ale) and my `Non-Alcoholic Spirits` (cocktail/margarita mixer syrups) are shopped alongside `Wine, Beer & Spirits`. Also non-alcoholic beer/wine/spirits (`WBS > Non-Alcoholic`, mine) vs `Drinks`.
5. **Frozen croissants / pains au chocolat / soda bread** (from `Frozen Pizza… > Breads`, dissolved) → belong in **Bakery**.
6. **Frozen meat-free "chicken" pieces** — my `Frozen Vegetarian & Meat-Free > Meat-Free Fillets, Pieces & Nuggets` deliberately parallels `Frozen Poultry > Chicken Nuggets & Goujons` / `Chicken Fillets`; a shopper searching "nuggets" wants both. Consolidation pass should decide whether meat-free stays a separate aisle or interleaves.
7. **Frozen fish** — `Frozen Foods > Frozen Fish & Seafood` (mine) vs `Fish & Seafood > Prepack Fresh Fish > Breaded Fish & Fish Cakes` / `Prawns & Shellfish` (another agent) — near-identical leaf names, chilled vs frozen.
8. **Ice / ice cubes** — trivial, but `Frozen Foods > Ice Cream & Desserts > Ice Cubes` could also sit under Drinks.
9. **Frozen ready meals** vs `Chilled Food > Ready Meals` (another agent) — parallel structure.

## Leaves I'm least sure about (keep vs dissolve)

- `Other & Mixed Fizzy Drinks` — kept against the brief (see deviation above). If the reviewer prefers, dissolve it and let the ~21 + Multipack items be individually classified.
- `Mini & Snacking Pizza` and `Mochi & Ice Cream Bites` — both kept as `map` where the brief's default leans dissolve; titles support them as real formats.
- `France` single wine leaf — could stay split by region.
- `Southern Fried & Takeaway Chicken` — borderline marketing ("takeaway"), but it's a genuine coated-chicken cluster distinct from plain fillets/nuggets and the brief said keep.
- `Non-Alcoholic Spirits` — mapped whole despite ~4 mixer syrups inside.

## Flags recommended (not acted on)

- `is_craft` (beer/cider) — replaces the dissolved `Craft Beer & Cider` branch.
- `is_kids` / portion flag for drinks — parallels the Kids Yogurts reasoning; would let `Kids Drinks` be derived rather than a category.
- No `is_alcohol_free` flag observed — the `Non-Alcoholic` branch is currently the only carrier of that attribute for beer/wine/spirits.
