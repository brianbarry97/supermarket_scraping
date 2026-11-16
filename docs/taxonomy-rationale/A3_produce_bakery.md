# A3 — Fruit & Vegetables, Bakery — rationale & escalations

## Summary

- Current leaves: 57 (Fruit & Vegetables 37, Bakery 20)
- Proposed leaves: 49 (Fruit & Vegetables 31, Bakery 18)
- Dispositions: 47 `map`, 10 `dissolve`

## Fruit & Vegetables

### Structure

Three aisles under the department: `Fruit`, `Vegetables`, `Salad Vegetables`, plus two
2-level leaves `Herbs` and `Fresh Flowers`.

### The `Salads` name collision — renamed to `Salad Vegetables`

`Fruit & Vegetables > Salads` is salad *vegetables* (cucumber, lettuce, tomatoes, leaf bags,
spring onions, sweetcorn). `Chilled Food > Salads` (A2) is prepared deli salads (coleslaw, potato
salad). Same word, different product. I renamed my `taxonomy_2` to **`Salad Vegetables`** so the
two never merge. Tomatoes stay here (not moved to `Vegetables`) per the project owner.

### Dissolves

- **`Fruit > Organic` (17)** — attribute dump, not a product type. `is_organic` backfilled to
  100%. Products are ordinary fruit (apples, pears, kiwis, limes, mango, oranges, peaches,
  pineapple, plums, watermelon, dates, avocados) and each needs per-item type inference against
  the frozen taxonomy.
- **`Vegetables > Organic Vegetables` (31)** — same. Products are ordinary veg (carrots, broccoli,
  cabbage, cauliflower, peppers, tomatoes, onions, leeks, kale, courgettes, cucumber, beetroot,
  sweet potato, fine beans, mushrooms, garlic, ginger, chillies). Per-item inference.
- **`Salads > Salad Dressing` (8)** — not produce at all. Chilled balsamic/caesar/honey-mustard
  dressings, croutons, and seed "salad toppers". Belongs in another department (see collisions).

### Non-obvious merges

- **Herbs three-way merge** — `Fresh Herbs` (12) + `Potted Herbs` (7) + `Prepack Herbs` (4) → one
  `Herbs` leaf. Cut vs growing is a packaging split. Caveat: `Prepack Herbs` is actually
  garlic/ginger/chilli *purees* — arguably a cooking-paste product type rather than herbs — but
  merged here per the project owner's instruction.
- **`Beetroot` (2) + `Parsnip, Swede & Turnip` (5)** → `Beetroot, Parsnip, Swede & Turnip`. Two
  tiny root-veg buckets; carrots and potatoes stay separate as they're large and distinct.
- **`Spinach` (1)** folded into `Cabbage, Broccoli & Leafy Greens` (was `Broccoli, Cauliflower &
  Cabbage`), which also absorbs kale.
- **`Potatoes` (2-level, 67)** → `Vegetables > Potatoes & Sweet Potatoes`. Renamed to give sweet
  potato an explicit home (sweet potato otherwise only existed inside the dissolved
  `Organic Vegetables`). Fresh-cut chip / peeled-potato packs sit here too.
- **`Peaches, Plums & Nectarines` → `Stone Fruit`**; **`Exotic Fruit` → `Exotic & Tropical
  Fruit`**; **`Citrus` → `Citrus Fruit`**; **`Exotic Vegetables` → `Speciality Vegetables`**
  (rename only, contents unchanged).

### New destination-only leaf

- **`Vegetables > Green Beans, Peas & Mangetout`** — no whole source bucket maps to it. It exists
  as the target for pod vegetables (fine beans, mangetout, sugar snap, edamame, baby corn) that
  are currently scattered inside the dissolved `Organic Vegetables` and inside `Prepared
  Vegetables`. `Prepared Vegetables` is mapped as a unit, so the pod veg inside it stay under
  `Prepared & Stir-Fry Vegetables` unless the later per-item pass reclassifies them — flagged in
  the map note.

### Leaves I'm less sure about (kept, not dissolved)

- **`Speciality Vegetables`** (from `Exotic Vegetables`, 12) — mild catch-all. Contents are
  coherent as "individually-sold less-common veg" (asparagus, celeriac, fennel, chicory, radish,
  mooli, fresh ginger/turmeric/lemongrass). Splitting into 10 one-item leaves is worse. Kept.
- **`Prepared & Stir-Fry Vegetables`** (from `Prepared Vegetables`, 50) — coherent as
  prepped/cut/stir-fry veg, but holds a few edge items: crispy-onion garnishes (condiment-ish)
  and single-serve snack tomato/pepper pots.
- **`Prepared Fruit`** (21) — mostly cut fruit pots and fruit salads; a handful of chia-pudding /
  overnight-oats pots that are really chilled breakfast/dessert.

### Cross-department collisions (Fruit & Vegetables)

| My product type | Also lives in | Owner |
|---|---|---|
| `Salads > Salad Dressing` (dressings) | `Food Cupboard > Condiments & Table Sauces > Dressings` | A4 |
| `Salads > Salad Dressing` (croutons) | `Food Cupboard > ...` (croutons / stuffing area) | A4 |
| `Salads > Salad Dressing` (seed "salad toppers") | `Health & Wellness > Nuts, Seeds & Dried Fruit > Nuts & Seeds` | A5/A6 |
| `Herbs` (fresh/potted) | `Food Cupboard > Packet Sauces, Stocks & Herbs > Herbs & Spices` (dried) | A4 |
| `Herbs` (garlic/ginger/chilli purees, ex-`Prepack Herbs`) | `Food Cupboard > Foods Of The World` pastes | A4 |
| `Vegetables > *` (fresh) | `Frozen Foods > Frozen Vegetables`; `Food Cupboard > Tins, Cans & Packets > Peas, Carrots & Corn` / `Dried Veg` | A4 / frozen owner |
| `Fruit > Prepared Fruit` (chia pudding / overnight oats) | `Milk, Yogurt, Butter & Eggs` chilled desserts / breakfast pots | A1? |
| `Prepared & Stir-Fry Vegetables` (veg soup/stew packs) | `Chilled Food > Soup` | A2 |

Resolution left to the consolidation pass — flagging only. In every case the distinction is
*state* (fresh vs dried vs frozen vs tinned) or *department convention*, not product type.

## Bakery

### Structure

Three aisles: `Bread` (7 leaves), `Morning Goods` (4), `Cakes & Treats` (7).

### The sourcing split — merged away

SuperValu splits bakery three ways by where/how it was made: `Fresh In Store Bakery` vs
`Packaged Cakes & Treats` vs `Bread`. That's a sourcing attribute, not identity. I merged across
it and kept the product type:

- `Fresh In Store Bakery > Rolls & Baguettes` + `Bread > Baps, Buns, Rolls` → `Bread > Rolls, Baps
  & Baguettes`.
- `Fresh In Store Bakery > Chilled Cakes` + `Packaged Cakes & Treats > Traditional Cakes` →
  `Cakes & Treats > Cakes`.

### Dissolves

- **`Bread > Gluten Free Bread` (1)** — attribute bucket, `is_gluten_free` backfilled. The one
  product (corn broghies) is a crispbread.
- **`Fresh In Store Bakery > Sharing Treats` (46)** and **`Single Treats` (29)** — portion /
  format marketing, not product type. Both are grab-bags of cookies, cupcakes, muffins,
  doughnuts, traybake slices, tarts, scones, croissants, danishes, biscuit cake. Per-item.
- **`Bread > Brack, Brioche, Croissant, Scone, Muffin` (28)** — the name lists five different
  product types. Dissolve; items go to `Soda & Fruit Bread` (brack), `Rolls, Baps & Baguettes`
  (brioche buns), `Croissants & Pastries`, `Scones & Teacakes`, `Cupcakes & Muffins`, `Cakes`
  (fruit cake).
- **`Fresh In Store Bakery > Bread Loaves` (49)** — verified against all 49 titles: white pan,
  brown pan, soda bread, sourdough boules/bloomers, vienna, focaccia, multiseed and seeded loaves
  all in one bucket. Same coherence failure as `Sharing Treats`. "In-store unsliced loaf" is a
  sourcing/format attribute; the products belong in the colour/type bread leaves
  (`Sliced White` is wrong for unsliced, so most go to `Brown & Wholemeal`, `Seeded & Sourdough`,
  `Soda & Fruit Bread` by per-item inference; a `Bakery Loaves` leaf was considered and rejected
  because it just re-creates the sourcing split under a new name).
- **`Packaged Cakes & Treats > Buns & Small Cakes` (77)** — verified against all 77 titles.
  Genuinely mixed: muffins, cupcakes, fairy/queen cakes, mini rolls, bakewell tarts, jam tarts,
  apple pies, brownies, cookies, traybake squares, battenberg, french fancies, viennese whirls,
  iced buns, hot cross buns. No plurality worth a wholesale map. Per-item.
- **`Packaged Cakes & Treats > Flans, Sponges & Meringue` (23)** — whole sponge cakes +
  meringue nests + flan/vol-au-vent pastry cases. Sponge cakes → `Cakes`; meringues and cases →
  `Meringues & Baking Cases`.

### Destination-only leaves (Bakery)

`Morning Goods > Croissants & Pastries`, `Scones & Teacakes`, `Doughnuts`, and
`Cakes & Treats > Cupcakes & Muffins`, `Tarts & Pies`, `Cookies, Brownies & Traybakes`,
`Meringues & Baking Cases` — no whole bucket maps to these; they receive the per-item output of
the six dissolved Bakery buckets above (~250 products).

### Non-obvious mapping calls

- **`Bread > Speciality, Health & Seeded Sliced Bread` (39) → `Seeded & Sourdough Bread`** —
  mapped as a unit despite the "Health/Speciality" marketing words, because the contents really
  are consistently seeded / multigrain / chia / spelt / sourdough sliced loaves. Caveat: a few
  corn crispbreads / broghies in it would sit better in `Bagels, Thins & Wraps`.
- **`Bread > Bake At Home, Naan, Pitta` (13) → `Pitta, Naan & Flatbreads`** — "Bake At Home" is a
  format word. Half the bucket is naan/pitta, half is part-baked baguettes/ciabatta/petits pains.
  Mapped rather than dissolved (all are speciality bread, small bucket); the part-baked items
  could alternatively land in `Rolls, Baps & Baguettes`.
- **`Bread > Soda Bread & Fruit Bread`** kept as one leaf — soda bread and barmbrack/fruit loaf
  are adjacent Irish products and the bucket is small and clean.
- **`Crumpets, Farls, Pancakes, Waffles`** placed under `Morning Goods`, not `Bread`.

### Cross-department collisions (Bakery)

| My product type | Also lives in | Owner |
|---|---|---|
| `Bread` (gluten-free loaves/rolls) + dissolved `Gluten Free Bread` + GF cakes | `Health & Wellness > Free From > Gluten Free Bakery & Baking` (79) + `Gluten Free Biscuits & Rice Cakes` (79) | A5/A6 |
| `Bread > Pitta, Naan & Flatbreads` (naan) | `Food Cupboard > Foods Of The World > Indian > Naan Bread & Poppadoms` | A4 |
| `Cakes & Treats > Tarts & Pies` (sweet pastry) | `Chilled Food > Savouries & Snacks > Pies & Pastries` / `Sausage Rolls` / `Quiche` (savoury pastry) | A2 |
| `Cakes & Treats > Cookies, Brownies & Traybakes` | `Food Cupboard > Biscuits > Luxury Biscuits & Shortbread` / `Everyday Biscuits` (packaged) | A4 |
| `Bread > Rolls, Baps & Baguettes` (garlic bread lands nearby) | `Chilled Food > Pizza & Garlic Bread > Garlic Bread`; `Frozen Foods > Frozen Pizza, Garlic Bread & Party > Breads` | A2 / frozen owner |
| `Cakes & Treats > Meringues & Baking Cases` (flan bases, pastry cases) | `Food Cupboard > Home Baking > Homebaking Mixes`; `Milk, Yogurt, Butter & Eggs > Butter & Spreads > Pastry` (raw pastry) | A4 / A1 |

## Recommended new flags

- No new dietary flag needed (`is_organic`, `is_gluten_free` already exist and are backfilled).
- Consider an `is_prepared` / `is_ready_to_eat` boolean so `Prepared Fruit`,
  `Prepared & Stir-Fry Vegetables` and prepped-veg items dissolved out of `Organic Vegetables`
  can be filtered without depending on the leaf name. Recommend only — not acted on.

## Top 3 escalations

1. **Free From duplication (gluten-free bakery).** My dissolved `Bakery > Gluten Free Bread` plus
   any gluten-free loaves/cakes in mapped buckets collide with `Health & Wellness > Free From >
   Gluten Free Bakery & Baking` (79) and `Gluten Free Biscuits & Rice Cakes` (79) — a large
   parallel department. The consolidation pass must decide the canonical home: product-type leaf
   in Bakery + `is_gluten_free` flag, vs. a standalone Free From department. Cannot be resolved
   inside my subtree.

2. **`Salads > Salad Dressing` (8) is entirely cross-department.** Chilled dressings → `Food
   Cupboard > Condiments & Table Sauces > Dressings` (A4); croutons and seed toppers also
   non-produce. Dissolved on my side with no target; A4 (and possibly A5/A6 for the seed toppers)
   needs to absorb it. Also note `Salad Dressing` under my `Salads` is itself the collision the
   project owner flagged with `Food Cupboard > Condiments & Table Sauces > Dressings`.

3. **Sweet vs savoury pastry boundary.** My `Cakes & Treats > Tarts & Pies` (sweet: apple/fruit
   tarts, bakewell, jam tarts, mince pies) sits right next to A2's `Chilled Food > Savouries &
   Snacks > Pies & Pastries` / `Sausage Rolls` / `Quiche`. Someone has to set the rule for which
   department owns a "pie" or "tart" — it's not resolvable within either subtree alone.
