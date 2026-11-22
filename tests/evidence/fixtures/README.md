# Evidence test fixtures

Each `*.json` file is a saved Firecrawl response shape: `markdown`, `json` (the schema-constrained
extraction) and `metadata` (`status_code`, `credits_used`). Tests replay them through a fake scraper,
so no network or API key is needed.

## Real captures (`live_*.json`)

Saved from the live Firecrawl API on 2026-11-02, one scrape each (5 credits):

| File | Page | Why it is here |
|------|------|----------------|
| `live_jacket_shell_lining.json` | Levi's Washed Cotton Field Jacket (altitude-sports.com) | Shell 100% cotton + Lining 100% polyester: the main fabric must be the shell |
| `live_tee_cotton_poly_blend.json` | Hooey Desert Dillo tee (academy.com) | 50% cotton / 50% polyester blend written as a sentence |

Saved from the live API on 2026-11-04 (one scrape each, 5 credits):

| File | Page | Why it is here |
|------|------|----------------|
| `live_linen_shirt_eur.json` | MUJI washed linen shirt (muji.eu) | 100% linen, EUR price, origin Cambodia |
| `live_sweater_multipart_sold_out.json` | J.Crew merino V-neck | Body / neck / trim compositions; the page says it has sold out and shows no price |
| `live_sweater_no_percentages_sold_out.json` | Everlane merino crew | Page says only "RWS-certified merino wool": no number, so natural_fiber_pct must be null |
| `live_dress_body_and_insert_sold_out.json` | Lolë Traverse dress (altitude-sports.com) | "92% Viscose 8% Elastane \| Insert : 95% Cotton 5% Elastane": insert is trim; sold out |
| `live_tee_extractor_says_not_product.json` | True Classic tee | Firecrawl's extractor wrongly said "not a product page". The page lists 8 other products' compositions, so the record must stay unavailable. The `json` here is reconstructed as `{"is_product_page": false}` because the client discards it on that path. |

## Synthetic fixtures (everything else)

Written by hand to mimic real page structure (bullet list, table, missing composition, blocked page,
non-product page, extractor miss, invented composition). Retailer names use placeholder `example.test`
domains. No real missing-composition or blocked page has been captured yet: every real page tried so
far was readable. Replace these when a real one turns up.

## Milestone 2 failure reproductions (synthetic)

Hand-written to reproduce the two failures in the Milestone 2 report. They are NOT live captures:
replace them with real captures of the Gap Factory and Levi's pages when Firecrawl credits allow.

| File | Reproduces | Expected |
|------|------------|----------|
| `gap_factory_garbled.json` | Double-encoded dashes (`Ã¢â‚¬â€œ`) next to "cotton blend" | Encoding repaired; no percentage, so `natural_fiber_pct` is null, confidence `ambiguous`, hint says "blend" |
| `levis_slash_no_percentages.json` | "Cotton/Denim/Polyester" | `natural_fiber_pct` null, `fibers_mentioned` = cotton, polyester in page order, hint says order is not a share |

## Live Gap Factory and Levi's captures (2026-11-22, one scrape each, 5 credits)

| File | Page | Result |
|------|------|--------|
| `live_gap_factory_straight_pid5245.json` | High Rise '90s Slim Straight Jeans | 93% cotton, 5% recycled cotton, 2% elastane, explicit |
| `live_gap_factory_soft_wear_pid1179.json` | Straight Jeans | "- 98% Cotton, 2% Spandex", explicit |
| `live_gap_factory_classic_straight.json` | Mid Rise Classic Straight Jeans | No fabric text in the scrape: composition missing, never guessed |
| `live_gap_factory_curvy_straight.json` | Mid Rise Curvy Classic Straight | Sold out; the page is not a product page, so unavailable |
| `live_levis_724_black.json` | 724 High Rise Straight, Black | 78% cotton, 21% polyester, 1% elastane |
| `live_levis_tailored_724_white.json` | Tailored 724 High Rise Straight, White | 97% cotton, 3% elastane |

None of these reproduced the Milestone 2 garbled text or the no-percentage "Cotton/Denim/Polyester"
line, so those two failures stay covered by the synthetic fixtures above.
