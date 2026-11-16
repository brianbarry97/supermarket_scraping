# A4_ambient — Food Cupboard — notes

## Leaf count / method

- Enumerated leaf paths from **`full_taxonomy.txt` lines 214–338 as authoritative** → **125 current leaf paths**
  (map.tsv has one row per path, plus header).
- The brief says 124. The single missing path is **`Foods Of The World > Thai > Thai Meal Kits` (1 product)** —
  present in `full_taxonomy.txt`, absent from `dept_extracts/A4_ambient.md`. Included it (mapped to `Thai > Meal Kits`).
- Per-leaf product counts differ slightly between the two input files (e.g. `Everyday Biscuits` 116 vs 115,
  `Crisps & Snacks` 243 vs 242, `Chocolate Bars` 351 both). Different scrape dates — harmless, flagging so the
  consolidation pass doesn't re-investigate.
- Left-hand `category_*` columns in map.tsv are generated **verbatim** from the raw paths (script `_gen.py`), so
  `Tomatoes, Passatas & Purée`, `Páté`, the `Sweetners` typo etc. join cleanly. Renames live only in `taxonomy_*`.

**Result: 112 taxonomy leaves. 118 map, 7 dissolve.**

## Dissolves (7)

| raw leaf | why |
|---|---|
| `Biscuits > Healthier & Breakfast Biscuits` (36) | "Healthier" marketing tier + genuinely mixed contents: breakfast biscuits (Belvita → new `Biscuits > Breakfast Biscuits` leaf), flapjacks + Nature Valley/Go Ahead/Fibre One bars (→ `Breakfast Cereals > Cereal Bars`). |
| `Breakfast Cereals > Healthier Cereals` (30) | "Healthier" marketing tier; ~half granola (→ `Muesli & Granola`), ~half bran/fibre/Special K flake cereal (→ `Cereals`). |
| `Chocolate & Sweets > Seasonal` (20) | Seasonal marketing bin — boxed chocolates, sweet bags, novelties, truffles all present; real type varies per item. |
| `Desserts & Sundries > Dessert Pots` (7) | Mixed: Ambrosia custard pots + rice-pudding pots, ~4/3 split. (Sibling `Custard & Custard Pots` and `Rice Pudding & Rice Pots` were coherent enough to map.) |
| `Foods Of The World > Italian > Premium Italian` (88) | Marketing tier — see dedicated section below. |
| `Foods Of The World > Tastes Of The World` (3) | Catch-all: tahini, harissa paste, hoisin/garlic stir-fry sauce. No coherent type. |
| `Tins, Cans & Packets > Other` (3) | Catch-all: artichoke hearts, cooked chestnuts, jarred green beans. |

### Premium Italian (88) — the big dissolve, checked product-type by product-type

Every product type inside it has an existing target leaf, so the orphan LLM pass has somewhere to put each item:

| product type in bucket | target leaf |
|---|---|
| dried pasta (Rummo range) | `Rice, Pasta & Noodles > Pasta` |
| pasta / pizza / bolognese sauces (Don Antonio, Rummo) | `Italian > Pasta & Cooking Sauces` |
| pesto (Rummo, Alce Nero) | `Italian > Pesto` |
| passata, chopped/peeled tomatoes, San Marzano | `Tinned Tomatoes > Passata` / `Chopped & Whole Tomatoes` |
| tomato purée/concentrate | `Tinned Tomatoes > Tomato Purée` |
| extra virgin olive oil, truffle oil | `Oils > Olive Oil` / `Seed & Nut Oil` |
| tinned tuna (Callipo) | `Tinned Fish > Tuna` |
| arborio/carnaroli rice, risotto, polenta, cous cous | `Rice, Pasta & Noodles > Rice & Grains` |
| breadsticks, flatbreads (I Bibanesi, Mario Fongo) | `Biscuits > Crackers & Crispbreads` |
| balsamic vinegar / glaze (La Vecchia, Vecchia Dispensa) | `Condiments & Table Sauces > Vinegar` |
| dried porcini | `Packet Sauces, Stocks & Herbs > Herbs & Spices` |
| tinned chickpeas / cannellini (Alce Nero) | `Tinned & Packet Foods > Beans & Pulses` |
| antipasti / caponata / bruschetta (Agromonte) | `Italian > Antipasti & Sundried Tomatoes` |
| stock/vegetable cubes | `Packet Sauces, Stocks & Herbs > Gravy & Stock` |

## Non-obvious merges / renames

- **`Biscuits`**: `Everyday Biscuits` (116), `Luxury Biscuits & Shortbread` (18) and `Multipacks & Kids Biscuits` (7)
  all → `Sweet Biscuits & Cookies`. "Everyday", "Luxury", "Multipack", "Kids" are tier/segment/packaging, not product
  types; contents of all three are sweet biscuits/cookies/shortbread. Kept `Crackers & Crispbreads` separate (real type)
  and added `Breakfast Biscuits` (real type, target for the Belvita-type SKUs from the dissolved bucket).
- **`Breakfast Cereals > Cereals` + `Family Cereals` → `Cereals`.** "Family" is a shopper segment and the two are
  near-duplicates (owner flagged this).
- **`Coffee > Decaf Instant Coffee` → `Instant Coffee`** and **`Tea > Decaffeinated` → `Tea Bags`.** "Decaf" is an
  attribute. There is currently **no `is_decaf` flag** — recommend adding one (see below) before these merges lose
  the signal.
- **`Home Baking > Icing Sugar` → `Home Baking > Icing & Frosting` (deliberate rename, not cosmetic).** The bucket is
  ready-made icing / frosting / fondant / cake covering (Betty Crocker, Cadbury, easy-melt), *not* icing sugar. This
  removes a real intra-department clash with `Sugar > Icing Sugar` (which is actual icing sugar + royal icing sugar
  and stays as-is).
- **`Hot Drinks`** (2-level leaf in the raw tree) promoted to `Hot Drinks > Hot Chocolate & Malted Drinks` for
  consistency with `Tea` / `Coffee` as sibling aisles. Marvel dried skimmed milk and Nesquik milkshake mix are minor
  impurities (9 SKUs total) — acceptable.
- **`Rice, Pasta & Noodles > Rice` → `Rice & Grains`** so couscous/polenta/quinoa (incl. those falling out of the
  Premium Italian dissolve) have a home.
- **`Tins, Cans & Packets` exploded** into five taxonomy_2 aisles: `Tinned & Packet Foods`, `Tinned Fish`,
  `Tinned Soup`, `Tinned Tomatoes`, `Instant Hot Snacks`. The 4-level branches (`Fish > {Tuna…}`,
  `Soups > {Ready To Heat…}`, `Instant Hot Snacks > {Noodle…}`, `Tomatoes, Passatas & Purée > {…}`) had the c4 as the
  real product type, so the c3 middle level was dropped per the depth rule.
- **`Foods Of The World` middle level dropped** everywhere: cuisine becomes taxonomy_2 (`Italian`, `Indian`, `Asian`,
  `Japanese`, `Thai`, `Mexican`), product type becomes taxonomy_3. `Asian > Accompaniments` + `Asian > Asian Sauces`
  merged into `Asian > Cooking Sauces & Ingredients` (both are soy/coconut/stir-fry/curry). `Japanese` (no c4 in raw)
  became a single `Japanese > Cooking Sauces & Ingredients` leaf.

## Overrides of the brief

- **`Tins, Cans & Packets > Meat` (6) — mapped, not dissolved.** The brief names it as a catch-all to dissolve. All
  6 SKUs are Fray Bentos tinned meat / meatballs / meat pies, and "Meat" does answer "what is this product". Mapped to
  `Tinned & Packet Foods > Tinned Meat & Meat Meals`. The consolidation pass can reverse this to a dissolve; the leaf
  should stay in the taxonomy regardless (it is the target the orphan pass would need).

## Cross-department collisions (for the consolidation pass)

| A4 leaf | collides with | owner |
|---|---|---|
| `Condiments & Table Sauces > Olives & Capers` | `Chilled Food > Páté, Olives & Dips > Olives` | A2 |
| `Condiments & Table Sauces > Salad Dressings` | `Fruit & Vegetables > Salads > Salad Dressing` | A3 |
| `Condiments & Table Sauces > Condiment Sauces` (cranberry etc.) | overlaps A2 chilled deli / A3 | A2/A3 |
| `Crisps… > Snacking Nuts & Dried Fruit` | `Health & Wellness > Nuts, Seeds & Dried Fruit > *` | A6 |
| `Crisps… > Dips & Salsa` (3, ambient) | `Chilled Food > Páté, Olives & Dips > Dips` | A2 |
| `Home Baking > Baking Nuts & Seeds` | `Health & Wellness > Nuts, Seeds & Dried Fruit` | A6 |
| `Home Baking > Baking Dried Fruit` | `Health & Wellness > Nuts, Seeds & Dried Fruit > Dried Fruit` | A6 |
| `Packet Sauces, Stocks & Herbs > Stuffing & Breadcrumbs` | `Chilled Food > Stuffing & Breadcrumbs` | A2 |
| `Tinned Soup > *` (Tinned/Packet/Cup Soup) | `Chilled Food > Soup` | A2 |
| `Italian > Pesto` (16) | `Chilled Food > Páté, Olives & Dips > Pesto` (10) — clean duplicate pair | A2 |
| `Indian > Breads & Poppadoms` | `Bakery > Bread > Bake At Home, Naan, Pitta` (Pataks naan in both) | Bakery owner |
| `Home Baking > Icing & Frosting` vs `Sugar > Icing Sugar` | intra-A4, resolved by rename (noted above) | A4 |
| `Mexican > Salsa, Beans & Sides` holds tortilla chips | duplicates `Crisps, Snacks, Nuts & Popcorn > Crisps & Snacks` | intra-A4 |
| `Asian` / `Japanese` / `Thai` `> Cooking Sauces & Ingredients` | three identically-named leaves; soy sauce / coconut milk sit in all three | intra-A4 (see escalation 1) |

## Unsure / borderline (kept, flag for review)

- `Tea > Speciality Tea` (10) — rooibos, matcha, earl grey, white tea. Distinct teas rather than one type; "Speciality"
  is borderline catch-all. Kept as a leaf; could be split into `Green, Fruit & Herbal Tea` + `Tea Bags`.
- `Desserts & Sundries > Dessert Sauces & Toppings` (17) — maple syrup + caramel/chocolate sauce + squirty cream +
  dessert topping. Mapped as one; mildly mixed.
- `Condiments & Table Sauces > Condiment Sauces` vs `Chutney & Relish` — cranberry sauce appears in both raw buckets;
  kept both leaves.

## Recommended new flags (recommend, not acted on)

- **`is_decaf`** — needed before `Decaf Instant Coffee`→`Instant Coffee` and `Tea > Decaffeinated`→`Tea Bags` lose the
  signal. ~7 SKUs affected but it's a real shopper filter.
- **`is_wholewheat` / `is_wholegrain`** — Rummo/Barilla wholewheat pasta, wholegrain rice, bran cereals are scattered;
  a flag would let those buckets dissolve cleanly.
- No `is_protein` flag: `Nature Valley Protein` bars and "high protein" granola/porridge exist but not in volumes that
  justify a `Protein` product type here — left folded into `Cereal Bars` / `Muesli & Granola` / `Porridge & Oats`.

## Top 5 escalations

1. **Cuisine-as-aisle re-creates the exact scatter this project fixes.** Following the owner's instruction (cuisine =
   taxonomy_2) puts soy sauce / coconut milk / stir-fry sauce in three identically-named leaves —
   `Asian`, `Japanese` and `Thai > Cooking Sauces & Ingredients`. A shopping agent still checks three places for one
   item. Recommend the consolidation pass consider folding the Japanese and Thai *ingredient* leaves into the pan-Asian
   one (keeping Thai/Japanese *curry pastes*, *meal kits* etc. distinct). Not acted on here.
2. **`Tins, Cans & Packets > Meat`** — overrode the instruction to dissolve (contents are coherent Fray Bentos tinned
   meat). Needs a ruling.
3. **Pesto duplicated across departments** — `Food Cupboard > Italian > Pesto` (16, ambient) and
   `Chilled Food > Páté, Olives & Dips > Pesto` (10, A2). Same product, temperature-split. Decide whether ambient and
   chilled pesto are one leaf.
4. **Nuts & dried fruit split three ways** — A4 `Crisps… > Snacking Nuts & Dried Fruit`, A4 `Home Baking > Baking
   Nuts & Seeds`, A4 `Home Baking > Baking Dried Fruit`, and A6 `Health & Wellness > Nuts, Seeds & Dried Fruit`.
   Four leaves for what a shopper sees as "nuts" and "dried fruit". Needs a cross-department rule (probably: baking
   vs snacking is a real use-context split; A6 health-positioned is the questionable one).
5. **Soup split across A4 and A2** — `Tinned Soup > {Tinned, Packet, Cup}` (A4) vs `Chilled Food > Soup` (A2, 53
   products, one flat leaf). Consolidation should decide whether format (tinned/packet/cup/chilled/fresh) is the
   taxonomy_3 axis for soup and who owns the parent.
