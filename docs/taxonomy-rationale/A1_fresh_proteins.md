# A1_fresh_proteins — notes

Departments owned: **Meat & Poultry, Fish & Seafood, Deli Counter**
Input: 44 current leaves / 766 products.
Output: **29 proposed leaves** (22 Meat & Poultry, 7 Fish & Seafood, 0 Deli Counter).
Dispositions: **36 map, 8 dissolve.** Of the 36 maps, 5 are cross-department (Deli Counter → A2 Chilled Food).

Deli Counter emits **no** `taxonomy_1` rows of its own — per the project owner it is not a real department and every path lands in A2's Chilled Food.

---

## Design decisions

### Merge the Butcher / Pre-pack sourcing level away (Beef, Bacon, Chicken, Pork, Lamb)
Butcher vs Pre-pack is a counter/packaging distinction, not a product type. Wherever both sub-trees carried the same cut level (Beef, Lamb) the cut survives and the sourcing level is dropped — `Beef > Butcher > Beef Steaks` + `Beef > Pre-pack > Beef Steaks` → `Beef > Steaks`. This alone collapses 11 beef leaves → 5 and 9 lamb leaves → 5.

Note: I renamed `Beef Steaks` → `Steaks` (the `Beef` parent already carries the species) and folded the beef/lamb `Bbq Meats` cut into **`Burgers, Grills & Meatballs`** — its contents are exclusively burgers, grillsteaks, koftas and meatballs, never a "BBQ" as such.

### Per-bucket dissolve calls (not per-species)
Butcher and Pre-pack for the same species have different content mixes, so they get different dispositions:

| Bucket | Call | Why |
|---|---|---|
| `Chicken & Poultry > Butcher` (13) | **map** → Fresh Chicken & Turkey | almost all raw fillets/legs; only ~3 strays |
| `Chicken & Poultry > Pre-pack` (94) | **dissolve** | ~25–35 breaded/kiev/goujon/nugget items are a large sub-population a shopper searches for by a different name; rest is raw cuts |
| `Pork > Butcher` (21) | **map** → Chops, Steaks & Roasts | chops/steaks/loin/belly/joints; only 2 rib racks stray |
| `Pork > Pre-pack` (22) | **dissolve** | ~3 mince + ~2 ribs mixed in; I define `Pork > Mince` and `Pork > Ribs` (beef and lamb both get a mince leaf — pork mince is a real search target) |
| `Bacon > Butcher` (6) | **dissolve** | 4 of 6 are actually *rashers*, 2 are ribs/joint — no single correct map |
| `Bacon > Pre-pack` (32) | **map** → Bacon Joints, Chops & Ribs | coherent: raw bacon/ham joints, fillets, loin, chops, medallions, ribs |

Every dissolve note names the destination leaves, and all of those leaves exist in `taxonomy.tsv`. Leaves fed **only** by a dissolve (`Breaded & Coated Poultry`, `Pork > Mince`, `Pork > Ribs`, `Prepared Meats > Marinated & Ready-to-Cook Meat`, all four Fish `Fresh Fish` / `Marinated & Ready-to-Cook Fish` types) are intentional — the downstream LLM pass needs a target.

### `Beef > Pre-pack > Organic` — dissolve
Attribute dump per the owner's brief. `is_organic` is already backfilled at 100% coverage, so nothing is lost. The 6 products (rib-eye/sirloin/striploin steak, steak mince, diced beef, burgers) need per-cut inference into the normal beef leaves.

### `Prepared By Our Butcher` (63) — dissolve
Genuine three-way mixed bag:
1. raw marinated/stuffed/wrapped/skewered meat → `Meat & Poultry > Prepared Meats > Marinated & Ready-to-Cook Meat` (a leaf I created for this)
2. **vegetable side dishes** (garlic wedges, luxury mash, potato gratin, beer-battered onion rings, roast veg, carrot & parsnip chips, curried cauliflower) — not meat at all → belong in A2's `Chilled Food > Ready Meals > Sides`
3. a few cooked ready-to-eat items → A2 chilled

### `Fish Counter` (38) and bare `Prepack Fresh Fish` (23) — dissolve
Both mix fin fish (salmon, white fish, whole/oily) with shellfish, and the bare Prepack bucket also mixes plain vs marinated. No coherent single target. They split across `Fresh Fish > {Salmon & Trout, White Fish, Whole & Oily Fish}`, `Shellfish & Seafood > Prawns, Crab & Shellfish`, and (bare Prepack only) `Prepared Fish > Marinated & Ready-to-Cook Fish`.

The three *named* Prepack Fresh Fish sub-leaves (`Breaded Fish & Fish Cakes`, `Prawns & Shellfish`, `Smoked & Ready To Eat Fish`) are each coherent and **map** cleanly.

### `Prepared By Our Fishmonger` (8) — map
All coated/crumbed prepared fresh fish + fishcakes → `Prepared Fish > Breaded Fish & Fishcakes`. Two items (smoked seafood gratin, white fish & salmon bake) are borderline ready-meal (A2) — noted in the row.

### `Sausage, Rasher & Pudding > Meat Free` (7) — map, renamed
Kept as a leaf but **renamed** `Meat Free` → `Meat-Free Sausages, Rashers & Pudding`. Bare "Meat Free" fails the dissolve test as a dietary-attribute label; the renamed leaf names the product and passes (same move as the spec's `Kids Yogurts`). The 7 items are a coherent set of plant-based breakfast items. Precedent: `Frozen Foods > Frozen Vegetarian > Burgers & Sausages` already treats meat-free bangers as a product type. **Open question for consolidation** — see escalation notes.

### `Slow Cooked` (1) — dissolve
One cooked ready-to-heat dish (lamb shanks in red wine gravy). Not worth a leaf. Most likely home is A2's `Chilled Food > Ready Meals`; fallback `Prepared Meats > Marinated & Ready-to-Cook Meat`.

### `Game` (6) — map
All duck. Renamed leaf `Duck & Game Birds` to leave headroom.

---

## Cross-department collisions (for the consolidation pass to resolve)

1. **Deli Counter → A2 Chilled Food (5 paths).** `Deli Counter > Cooked Meats > {Ham, Poultry, Beef & Lucheon Meats}` duplicate `Chilled Food > Sliced Cooked Meats > {Ham, Poultry, Beef & Luncheon Meats}` (note the `Lucheon`/`Luncheon` typo — left side keeps it, right side corrected). `Deli Counter > Cooked Meats > Speciality` (chorizo, serrano, ox tongue, "blacky ham") mapped to `Chilled Food > Sliced Cooked Meats > Continental Meats` — **partial fit**: chorizo/serrano are continental charcuterie, ox tongue is not. `Deli Counter > Made In Store Salads` → `Chilled Food > Salads > Prepared Salads`. **A2 owns all five destination leaves and must confirm the names survive their own pass.**

2. **`Prepared By Our Butcher` vegetable sides → A2 Chilled `Ready Meals > Sides`.** Needs an A1/A2 boundary ruling: does a "prepared meat" aisle live with the raw meat (my `Meat & Poultry > Prepared Meats`) or with chilled prepared food (A2)? I put the raw marinated meat under Meat & Poultry; the veg sides and cooked dishes are clearly A2's.

3. **Coated/breaded proteins split three ways.** My `Chicken & Poultry > Breaded & Coated Poultry`, my `Prepared Fish > Breaded Fish & Fishcakes`, and `Frozen Foods > Frozen Fish & Seafood > {Breaded Fillets & Steaks, Battered Fillets & Steaks, Fish Fingers, Fish Cakes}` (+ `Frozen Vegetarian > Burgers & Sausages`). The consolidation pass needs **one consistent rule** on whether coating is a product type or an attribute, or fresh vs frozen will diverge.

4. **Meat-free / plant-based** is scattered: my `Meat-Free Sausages, Rashers & Pudding`, `Frozen Foods > Frozen Vegetarian`, `Chilled Food > Ready Meals > Vegetarian & Vegan Ready Meals`. A cross-department `Vegetarian & Meat Alternatives` aisle may be the right call — flag for whoever owns the meat-alternatives question.

5. **Offal** has no cross-species home. Only `Lamb > Butcher > Offal` is a dedicated bucket; beef oxtail sits in `Beef > Butcher > Roasts` and ox tongue in Deli. I kept `Meat & Poultry > Lamb > Offal`. Consider a species-neutral `Meat & Poultry > Offal` aisle in the frozen taxonomy.

6. **Fresh salmon darnes** are the single most scattered product in my departments: `Fish Counter`, bare `Prepack Fresh Fish`, and `Prepack Fresh Fish` marinated variants all carry them. My dissolve of the two loose buckets + the `Salmon & Trout` leaf should consolidate them, but the LLM pass must be consistent about plain vs marinated (Fresh Fish vs Prepared Fish).

7. **`Chilled Food > Snacking > Single Serve Burgers & Grills`** (A2) overlaps my `Beef > Burgers, Grills & Meatballs`. Single-serve chilled burgers vs raw multipack burgers — flag for A2/A1 to decide the split line.

---

## Leaves I'm least sure about

- **`Pork > Ribs` as its own leaf** — only ~4 products total (2 stray from Butcher, ~2 from Pre-pack dissolve). Defensible for parallelism with the search target "pork ribs", but the consolidation pass may prefer to fold it into `Chops, Steaks & Roasts`.
- **`Prepared Fish > Marinated & Ready-to-Cook Fish`** — fed only by the bare `Prepack Fresh Fish` dissolve. If that dissolve produces very few marinated items, this leaf could be dropped and its contents merged into `Salmon & Trout` / `Shellfish & Seafood`.
- **`Prepared Meats > Marinated & Ready-to-Cook Meat`** — depends on escalation #2. If the consolidation pass decides prepared meat belongs in A2 chilled, this whole aisle (`Prepared Meats`) disappears and the `Prepared By Our Butcher` / `Slow Cooked` dissolves retarget.
- **`Meat-Free Sausages, Rashers & Pudding`** — keep-vs-dissolve-vs-move-to-a-vegetarian-aisle. I chose keep+rename; low confidence.
- **`Game > Duck & Game Birds`** — 6 items, all duck, several are cooked/prepared (crispy duck with pancakes, confit). Could arguably split cooked duck to A2.

---

## Flag recommendations (recommend, not acting)

- **`is_breaded_or_coated`** (boolean) — would let breaded poultry / breaded fish / fish fingers stay as an attribute on the raw product type instead of forcing separate leaves and three-way divergence (escalation #3). Currently there is no such flag, so I had to create coating leaves.
- **`is_marinated` / `is_seasoned`** (boolean) — same rationale for `Prepared Meats > Marinated & Ready-to-Cook Meat` and `Prepared Fish > Marinated & Ready-to-Cook Fish`. Would shrink the orphan set materially.
- **`is_ready_to_eat` / `is_cooked`** (boolean) — distinguishes deli cooked meats and smoked fish (eat as-is) from raw cuts, and would help route `Slow Cooked` / cooked items out of `Prepared By Our Butcher`.
- **`is_meat_free` / `is_plant_based`** (boolean) — nothing currently marks the 7 meat-free breakfast items or their frozen/chilled cousins; a flag would make a cross-department "meat alternatives" grouping trivial (escalation #4).
- **`protein_species`** (enum: beef / pork / lamb / chicken / turkey / duck / fish / none) — cheap to derive from title, and would make the beef/lamb/pork cut leaves collapsible to a single shared cut taxonomy (`Steaks`, `Mince`, `Roasts`, `Stewing & Diced`) with species as a facet rather than a `taxonomy_2`.
