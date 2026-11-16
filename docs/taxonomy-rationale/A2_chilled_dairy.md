# A2_chilled_dairy — notes

Departments: **Cheese**, **Chilled Food**, **Milk, Yogurt, Butter & Eggs**.
94 current leaf paths → 66 target leaves. 81 `map`, 13 `dissolve`.

New dissolve **target** leaves (receive products from the per-product pass, no `map` row points at them):
`Chilled Food > Meat Alternatives`, `Milk, Yogurt, Butter & Eggs > Chilled Desserts`,
`Milk, Yogurt, Butter & Eggs > Yogurts > Protein Yogurt`.

---

## Yogurts — the redesign (priority)

Greek/skyr yogurt was scattered across 7 sibling buckets. New shape — 5 descriptive leaves + a
separate `Chilled Desserts` aisle:

| new leaf | what lands here |
|---|---|
| Natural & Greek Yogurt | natural / Greek / Greek-style / skyr / Icelandic-style **plain** yogurt, any fat level, incl. plain protein-strained |
| Fruit & Flavoured Yogurt | fruit / vanilla / flavoured pots & multipacks, corner/granola styles |
| Protein Yogurt | yogurt/skyr/quark/kvarg **positioned as high-protein** (flavoured or natural) — kept as a real type, see flag rec below |
| Kids Yogurts | children's pots, fromage frais, pouches, tubes — survives, format IS the identity |
| Yogurt & Kefir Drinks | drinking yogurt, kefir drinks, probiotic shots (merges `Health & Kefir Drinks` + `Yogurt Drinks`) |
| Chilled Desserts (own aisle) | rice pudding, mousse, trifle, cheesecake, crème brûlée/caramel, tiramisu, chocolate pots, chilled pancakes |

**Dissolved (marketing tier / attribute / mixed):**
- `Everyday Yogurts` (3 leaf paths): NOT dissolved — each child is internally coherent, so mapped.
  `> Everyday Yogurts` (greek-style + skyr) → Natural & Greek; `> Multipacks` and `> Single Pots`
  (fruit/flavoured) → Fruit & Flavoured. This empties the "Everyday" tier cleanly without orphans.
- `Luxury Yogurts & Desserts` → **dissolve**. Genuinely mixed: real chilled desserts +
  luxury fruit yogurts + luxury greek yogurts. Splits 3 ways (Chilled Desserts / Fruit & Flavoured /
  Natural & Greek). This is the largest single orphan bucket (73).
- `Active Health` → **dissolve**. Benefit tier: Activia + Killowen fruit yogurts, Benecol greek-style,
  kefir, Muller Light. Splits Fruit & Flavoured / Natural & Greek / Yogurt & Kefir Drinks.
- `Organic` → **dissolve** (is_organic backfilled). Glenisk greek-style / natural / fruit. Splits
  Natural & Greek / Fruit & Flavoured.
- `Low Fat & Fat Free` → **dissolve** (is_low_fat backfilled). Fage 0% (natural/greek), Muller Light
  (flavoured), Muller Rice (dessert).
- `Protein` → **dissolve**. 91 products, heavily contaminated: protein yogurt/skyr/quark **plus**
  protein mousse/pudding (→ Chilled Desserts), protein shakes/drinks (→ Yogurt & Kefir Drinks),
  energy/protein balls (→ Health & Wellness, another dept), protein pancakes. Only the strained-yogurt
  subset lands in `Protein Yogurt`.

**Flag recommendation — `is_protein`.** "Protein yogurt" is now a genuine distinct product type
(strained high-protein yogurt/skyr/quark, distinct texture and use), so `Protein Yogurt` survives as a
leaf. But there is no `is_protein` flag, and protein positioning also spans `Fresh Milk > Protein &
Omega Milks` and protein desserts/drinks. Recommend adding `is_protein` so the attribute is queryable
across milk/yogurt/dessert without a dedicated bucket per department.

---

## Cheese

Counter/pre-pack sourcing split removed. Owner-mandated survivors are the cheese **types**
(`Cheddar`, `Continental & Speciality Cheese`, `Goats & Sheep Cheese`) plus the functional/format
leaves (`Cooking Cheese`, `Cottage & Cream Cheese`, `Grated & Sliced`, processed slices, snacks,
accompaniments).

- `Counter Cheese > Blue Cheese` → mapped into `Continental & Speciality Cheese`, **not** a new
  `Blue Cheese` leaf. Blue isn't on the owner's survivor list, and the flat `Continental & Speciality
  Cheese` bucket (mapped wholesale) already contains cashel blue, saint agur, cambozola, gorgonzola,
  roquefort — a separate Blue leaf would be contaminated on day one by a bucket I map as a unit.
- **Known residue inside the mandated pair:** the flat `Continental & Speciality Cheese` bucket also
  holds `supervalu goats cheese 125g`, `goats cheese with honey`, `sol manchego`, `manchego pdo`,
  `ossau iraty` — sheep/goat cheeses that will sit outside the `Goats & Sheep Cheese` leaf. Both
  leaves are owner-mandated so I don't fight it; flag for a later per-product cleanup.
- `Counter Cheese > Hard Cheese` → **dissolve**. Genuinely split between Cheddar (Dubliner, Wexford,
  Cheese Mongers cheddar) and Continental (gouda, edam, parmesan, red leicester, jarlsberg).
- `Counter Cheese > Soft Cheese` → mapped to `Continental & Speciality Cheese` (~15/17 fit; 2
  quince-paste strays are accompaniments).
- `Lactose & Dairy Free` → **dissolve** (is_dairy_free backfilled). Vegan blocks/slices/spreads +
  lactose-free cheddar span 4 type leaves.
- `Cheeseboards & Selections` → **dissolve**. Mixed: gift boxes, bake-in-box camembert/gouda
  (party/cooking), flavoured cheddar.
- `Grated & Sliced` kept as a leaf — pre-grated/sliced is a real purchase intent for cooking &
  sandwiches, not just packaging.

---

## Chilled Food

- **`Ready Meals` collapsed to 2 portion leaves + Sushi + Side Dishes.** `Ready Meals For 1 & 2`
  (absorbs For 1, For 2, Other Meals, Healthier) and `Family Ready Meals`. Portion format IS the
  purchase distinction for ready meals (SPEC blesses format when format is identity); a single
  mega-leaf would be the defect inverted.
  - `Ready Meals > Healthier` → **map** (not dissolve). Dissolve test applied: the bucket is 24/24
    chilled ready meals — bad ("benefit claim") name, coherent contents, exactly the
    `Beef > Pre-pack > Beef Steaks` case. Owner only gave a *verdict* to dissolve for `Low Fat Milk`
    and `Organic`; for `Healthier` the instruction was "apply the dissolve test", i.e. delegation.
    Recommend an `is_healthier` / lifestyle flag if the health positioning is worth keeping.
  - Same reasoning: `Butter & Spreads > Cholesterol Lowering` → map to `Dairy Spreads` (all buttery
    spreads), recommend `is_cholesterol_lowering` flag.
- `Ready Meals > Vegetarian & Vegan Ready Meals` → **dissolve**. Mixes veg ready meals + tofu +
  falafel + meat-free sausages/burgers + boxty + Quorn pieces. New `Chilled Food > Meat Alternatives`
  leaf created as the target for the non-ready-meal portion; there is currently no chilled
  meat-alternatives home in SuperValu's tree (only Frozen / Free From / Meat & Poultry > Meat Free).
- `Snacking > Other Snacks` → map to new `Snacking > Meat Snacks` (coherent: jerky, Peperami, chicken
  bites — catch-all name only).
- `Party Foods` (3 products) → map to `Savouries & Snacks > Pies & Pastries` (2 vol-au-vents; 1
  filo-prawn stray) — cheaper than dissolving 3 items.
- `Tapenades` (2) folded into `Olives & Antipasti`.

### Deli Counter inbound (A1 → my leaves) — all receive cleanly
| A1 source | my target | note |
|---|---|---|
| `Deli Counter > Cooked Meats > Ham` | `Sliced Cooked Meats > Ham` | ok |
| `Deli Counter > Cooked Meats > Poultry` | `Sliced Cooked Meats > Poultry` | ok |
| `Deli Counter > Cooked Meats > Beef & Luncheon Meats` | `Sliced Cooked Meats > Beef & Luncheon Meats` | **spelling**: current SuperValu leaf is `Beef & Lucheon Meats` [sic]; my taxonomy uses the correct `Luncheon`. Consolidation pass should standardise on `Luncheon`. |
| `Deli Counter > Cooked Meats > Speciality` | `Sliced Cooked Meats > Continental Meats` | no `Speciality` leaf created (SPEC names it a catch-all). If A1's "Speciality" is mostly roast beef/pastrami it may belong in `Beef & Luncheon Meats` instead — recommend A1 route per-product or the consolidation pass split it. |
| `Deli Counter > Made In Store Salads` | `Salads > Prepared Salads` | ok |

---

## Milk / Fresh Milk

- `Low Fat Milk` → **dissolve** (is_low_fat backfilled), per owner verdict. The bucket is genuinely
  mixed — it contains `arrabawn whole milk 2l` and `dawn ballinahina whole milk 1l` — and the
  surviving `Skimmed Milk` leaf **already holds** 1%/light milk in the current data (`clona 1 percent
  light milk`, `dawn ballinahina 1 percent light milk`, `snowcream milk light 1 percent`, etc.), so
  the design is coherent: Whole and Skimmed are the two surviving fat tiers and each low-fat product
  routes to one of them with `is_low_fat` intact.
  *(Considered and rejected: a new `Low Fat & Semi-Skimmed Milk` survivor leaf — no leaf the owner
  asked for, and it duplicates what Skimmed already absorbs.)*
- `Organic Milk` → dissolve (is_organic; 2 items → Whole / Skimmed).
- `Speciality Milk` → dissolve (catch-all "Speciality"; 3 items: vitamin-enriched, UHT long-life,
  Mighty Milk). If UHT/long-life milk grows, a `Long-life Milk` leaf would be justified.
- `Protein & Omega Milks` → **survives** as `Protein & Omega Milk` (descriptive; recommend
  `is_protein`).
- `Flavoured`, `Buttermilk`, `Goats Milk`, `Whole Milk`, `Skimmed Milk` → map unchanged.

## Cream & Custard
Consolidated 8 → 4: `Fresh Cream` (single+double), `Whipped & Aerosol Cream` (whipped + long-life
spray), `Sour Cream & Crème Fraîche` (sour/cooking + crème fraîche), `Fresh Custard`.
`Alternative Cream` (Elmlea plant) → moved out to `Milk & Yogurt Alternatives`.

## Butter & Spreads
`Block Butter`, `Spreadable Butter`, `Dairy Spreads`, `Cooking & Baking Fats` map unchanged.
`Cholesterol Lowering` → `Dairy Spreads` (see flag rec above).
`Pastry` → `Chilled Pastry & Dough` — **not butter**; it's chilled ready-rolled pastry / croissant
dough (+ 1 cookie-dough stray). Kept in this aisle because there is no chilled-pastry home elsewhere
(Frozen has "Baking Pastry", Food Cupboard "Home Baking" is ambient). Cross-dept flag below.

## Eggs
`Free Range` (incl. free-range liquid egg), `Standard` (barn/mixed-weight) survive.
`Organic` → dissolve (is_organic; 2 items, both *liquid egg white* not shell eggs).

## Dairy & Lactose Free → `Milk & Yogurt Alternatives` aisle
3 leaves: `Milk & Cream Alternatives`, `Yogurt Alternatives`, `Butter & Spread Alternatives`
(the parent-level `Dairy & Lactose Free` leaf = Flora Plant / Naturli vegan butter).
Kept as a distinct alternatives aisle (standard practice; `is_dairy_free` also on the flag).

---

## Cross-department collisions (consolidation pass to resolve)

| my leaf | collides with | owner |
|---|---|---|
| `Chilled Food > Soup` | `Food Cupboard > Tins, Cans & Packets > Soups` (Cup & Instant / Packets / Ready To Heat) | A4 |
| `Chilled Food > Fresh Pasta & Sauces > Fresh Pasta` | `Food Cupboard > Rice, Pasta & Noodles > Pasta` | A4 |
| `Chilled Food > Fresh Pasta & Sauces > Fresh Sauces` | `Food Cupboard > Foods Of The World > Italian > Italian Sauces` | A4 |
| `Chilled Food > Páté, Olives & Dips > Olives & Antipasti` | `Food Cupboard > Condiments & Table Sauces > Olives` | A4 |
| `Chilled Food > Páté, Olives & Dips > Fresh Pesto` | `Food Cupboard > Foods Of The World > Italian > Pesto` | A4 |
| `Chilled Food > Páté, Olives & Dips > Dips` | `Food Cupboard > Crisps, Snacks, Nuts & Popcorn > Dips` | A4 |
| `Chilled Food > Stuffing & Breadcrumbs` | `Food Cupboard > Packet Sauces, Stocks & Herbs > Stuffing & Breadcrumbs` | A4 |
| `Milk... > Cream & Custard > Fresh Custard` | `Food Cupboard > Desserts & Sundries > Custard & Custard Pots` | A4 |
| `Milk... > Chilled Desserts` | `Food Cupboard > Desserts & Sundries` (Dessert Pots, Rice Pudding & Rice Pots, Jelly) | A4 |
| `Cheese > Cheese Accompaniments` | `Food Cupboard > Biscuits > Crackers & Savoury Biscuits`; `Condiments > Chutney & Relish` | A4 |
| `Milk... > Butter & Spreads > Chilled Pastry & Dough` | `Frozen Foods > Frozen Pastry, Pies & Savouries > Baking Pastry`; `Food Cupboard > Home Baking` | A4 / A? |
| `Chilled Food > Meat Alternatives` | `Frozen Foods > Frozen Vegetarian`; `Health & Wellness > Free From`; `Meat & Poultry > Sausage, Rasher & Pudding > Meat Free` | A1 / others |
| `Milk... > Milk & Yogurt Alternatives` | `Health & Wellness > Free From > Dairy Free` | A? |
| `Chilled Food > Pizza & Garlic Bread > Chilled Pizza` | `Frozen Foods > Frozen Pizza, Garlic Bread & Party` | A? |
| `Chilled Food > Pizza & Garlic Bread > Garlic Bread` | `Bakery > Fresh In Store Bakery`; `Frozen ... > Breads` | A? |
| `Chilled Food > Snacking > Meat Snacks` | `Food Cupboard > Crisps, Snacks, Nuts & Popcorn` (jerky/Peperami sometimes ambient) | A4 |

---

## Flag recommendations (recommend, not acted on)
- **`is_protein`** — protein milk / protein yogurt / protein desserts span 3 aisles; no flag exists.
- **`is_cholesterol_lowering`** — Benecol/Proactiv spreads + Benecol yogurt drinks; dissolving/merging
  their buckets loses the only signal.
- **`is_healthier` / lifestyle tier** — if the "Healthier" / "Fit Foods" / "Clean Cut" ready-meal and
  "Muller Light" positioning is worth keeping queryable after the buckets are dissolved/merged.

## Leaves I'm genuinely unsure about
- `Cheese > Cheese Accompaniments` — kept as a coherent purpose-built range, but it's crackers +
  chutney + fruit paste, none of which is cheese. Could equally be dispersed into Food Cupboard.
- `Milk... > Chilled Desserts` as its own aisle vs. a child of `Yogurts` — went with its own aisle
  because SuperValu's own "Luxury Yogurts & Desserts" and the volume (rice pud + mousse + trifle +
  cheesecake scattered across 3 dissolved buckets) justify it.
- `Cheese > Grated & Sliced` vs. dispersing into the type leaves — kept (purchase intent), flag if
  the consolidation pass prefers type-first.
