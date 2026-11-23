# Consolidated recommendation eligibility and failure audit

Sources: QuickShop/B0/B1 from `eval_20261122_190556.json`; all 20 B2 answers from `eval_20261123_061857.json`. New B2 replaces the earlier B2 data. There are 150 ranked recommendation/sourcing entries across 69 successful selected executions; 11 failed executions are excluded. These are cross-run results, not a simultaneous controlled experiment. No live verification or paid calls were performed.

Companions: `eligibility_audit_eval_20261122_190556.csv` (150 item rows) and `.json` (evidence, current heuristic signals and summaries). Legacy filenames are retained, but each row records its source file. The main analysis companion contains 80 selected system/query executions, not 100 pooled old/new executions.

## Method

- Count all ranked recommendation/sourcing entries, including non-actionable suggestions, but exclude rejected sections and next-step lists. Totals: QuickShop 48, B0 3, B1 42, B2 57. B2 includes 18 answers with three entries, one with two (d2q19), and one with one (d2q23).
- Screen URL destinations before seller eligibility: homepages, category/filter pages, marketplace search pages, and saved extractor non-product rejections receive `not_a_product`. This flag means the supplied destination is not an individual offer; it does NOT mean the named garment cannot exist. One B1 generic Amazon blouse remains unresolved.
- For product-like entries with identifiable named merchants, use current `check_merchant` and `_score_legitimacy`, threshold >=3, using available actual hostnames. Do not manufacture real sellers from B0's illustrative catalog or assume that marketplace protection authenticates a seller.
- Preserve missing final links even where a same-item QuickShop score log supplies the URL. Retain unavailable/missing evidence separately from proof of a false claim. Baselines do not save comparable page-evidence records.
- Raw named-merchant checks for the new B2 are additionally reported as a sensitivity check, including non-product destinations. These are NOT product eligibility counts or authenticated seller identities.

## Seller-gate results

| Measure | QuickShop | B0 | B1 | B2 |
|---|---:|---:|---:|---:|
| Recommendation/sourcing entries | 48 | 3 | 42 | 57 |
| Product-like entries passing the current heuristic gate | 44 | 0 | 0 | 0 |
| Product-like entries rejected by the gate (NOT proven unsafe) | 0 | 0 | 1 | 4 |
| Gate not applicable: non-product destination | 4 | 0 | 40 | 53 |
| Gate not assessable: synthetic/unclear identity | 0 | 3 | 1 | 0 |

QuickShop's 44 passes differ from its original 48 eligible score outputs because four entries are excluded as non-products. B2 has only four product-like URLs, all naming Quince, which the current merchant helper rejects. This is an allowlist limitation, not evidence that Quince is unsafe.

## Mutually exclusive primary outcomes

Priority: non-product -> not assessable -> gate rejected -> other issue/evidence gap -> no flagged issue. Each column sums to its total.

| Measure | QuickShop | B0 | B1 | B2 |
|---|---:|---:|---:|---:|
| Not a product destination | 4 | 0 | 40 | 53 |
| Merchant gate rejected ('unsafe' proxy only) | 0 | 0 | 1 | 4 |
| Not assessable | 0 | 3 | 1 | 0 |
| Other failures / evidence gaps | 28 | 0 | 0 | 0 |
| No flagged issue in limited offline checks | 16 | 0 | 0 | 0 |
| Total | 48 | 3 | 42 | 57 |

The B2 'other failures' bucket is zero because destination failures/gate rejection take priority, NOT because its answers have no other problems. The overlapping tags below retain its evidence gaps. QuickShop's 16 unflagged entries are not certified safe or correct. These counts cannot establish a fair quality ranking because only QuickShop saved native page evidence.

## Common failure tags (overlapping)

Rows overlap and MUST NOT be summed. Zero observed HTTP/claim-conflict errors for baselines does not establish that the pages or claims are correct: they were not independently read.

| Measure | QuickShop | B0 | B1 | B2 |
|---|---:|---:|---:|---:|
| Non-product destination / extractor rejection | 4 | 0 | 40 | 53 |
| Only a homepage supplied | 0 | 0 | 0 | 47 |
| Unclear product identity | 0 | 0 | 1 | 0 |
| Illustrative catalog, not a real assessable seller | 0 | 3 | 0 | 0 |
| Product-like entry rejected by merchant gate | 0 | 0 | 1 | 4 |
| No link supplied in final answer | 7 | 3 | 42 | 0 |
| Unresolved grounding redirect | 0 | 0 | 0 | 0 |
| No displayed numeric product price | 0 | 0 | 42 | 0 |
| Displayed price only approximate / a range | 0 | 0 | 0 | 52 |
| No matching usable saved page record | 11 | 3 | 42 | 57 |
| No structured saved natural-fiber share >=50% | 20 | 3 | 42 | 57 |
| No matching exact USD page-price evidence | 15 | 3 | 42 | 57 |
| Scoring fiber share conflicts with saved value | 2 | 0 | 0 | 0 |
| Unverified EUR-to-USD conversion | 2 | 0 | 0 | 0 |
| Recommended URL's saved read returned HTTP 404 | 2 | 0 | 0 | 0 |
| Explicit requested-size mismatch in URL | 1 | 0 | 0 | 0 |
| Ethical-sourcing requirement not substantiated | 2 | 0 | 0 | 3 |
| Incidental substring counted as known brand | 1 | 0 | 0 | 0 |
| Displayed retail/sale prices exceed budget | 0 | 0 | 0 | 1 |
| Exact price equals strict 'under' threshold | 0 | 0 | 0 | 1 |
| Full-suit price versus separates not established | 0 | 0 | 0 | 1 |

## New B2: destination and pricing audit

| Destination | Entries |
|---|---:|
| Retailer/marketplace homepage | 47 |
| Outerwear category/collection | 3 |
| Marketplace search/results | 3 |
| Individual product-like URL | 4 |
| Total | 57 |

All four product-like URLs belong to Quince: three trousers in d2q20 and one cashmere sweater in d2q23. They were not fetched live. The 47 homepages and six category/search destinations are not individual purchasable offers even when the answer names a garment.

- 52/57 prices are approximate or ranges; the five exact displayed prices are d2q2 #2 ($35), d2q20 #1–3 ($89.90/$99.90/$80), and d2q23 #1 ($50). None has independent saved page-price verification.
- d2q19 #2 quotes $299 retail / roughly $224 sale for a $200 request, without establishing an in-budget offer.
- d2q22 #1 simultaneously quotes an approximate full-suit price and a jacket-only price with trousers sold separately; full-set cost is unclear.
- d2q23 #1 is exactly $50, not strictly under $50. This boundary flag is distinct from the stock evaluator's inclusive <= budget convention.
- d2q24 gives three secondhand search routes, and d2q25 gives three marketplace-sourcing suggestions, not specific verified jackets/blouses.
- d2q17's ethical-sourcing claims are not substantiated by saved product/source evidence.

The new B2 file contains answer text, elapsed time and exit code, but no provider/model identity, native-search calls, source annotations, or usage/cost record. Native grounding cannot be confirmed from prose or response latency alone.

## Why the 'unsafe' count is misleading

After destination screening, the four B2 product-like entries all name Quince and are rejected by the current allowlist heuristic. They are NOT four confirmed unsafe products. As a sensitivity check, applying the name heuristic to every B2 entry regardless of destination yields 26 passes and 31 rejections; these are seller-name claims, not eligible offers.

The superseded earlier B2 audit had 8 passes and 7 rejections across 15 entries. Those counts are not pooled into current tables. Its rejected names (Lands' End, Dockers, Los Angeles Apparel, L.L.Bean and Huckberry) illustrated allowlist blind spots, not actual danger.

The reverse error persists in QuickShop: Dalle Piane Cashmere passes because `hm` appears inside 'cashmere', accidentally matching H&M. The helper then supplies known-brand defaults of 10,000 reviews and a return-policy signal. This is one observed false brand match, not an exhaustive matcher audit.

Confirmed unsafe sellers: not established. No merchant/scoring code or brand list was changed to improve these counts.

## Unchanged QuickShop examples

- Non-products: Walmart henley category (d2q14 #1), Levi's filter/category (d2q15 #1), Macy's category (d2q20 #3), plus a J.Crew extractor rejection (d2q3 #4). An extractor rejection is not independently confirmed truth.
- Missing final links: all three d2q7 scarves, both d2q11 coats and both d2q13 coats; same-item tool logs supply their URLs.
- Recommended-item 404s: Everlane oxford d2q3 #5 and Everlane tunic d2q5 #3.
- Structured material conflicts: Gap tee d2q2 #3 and Banana Republic merino d2q8 #1 are scored as 100 despite structured page fiber share 0. Raw text suggests parser limitations, not proof of synthetic garments.
- Size mismatch: Target d2q23 #2 specifies 2X despite the recorded clarification answer L.

## Separate QuickShop pipeline failures (all candidates)

| Event / record type | Count |
|---|---:|
| Returned page records | 100 |
| OK / partial / unavailable | 36 / 41 / 23 |
| Unavailable: not a product page | 14 |
| Unavailable: HTTP 404 | 8 |
| Unavailable: HTTP 500 after four tries | 1 |
| Partial: composition ambiguous only | 20 |
| Partial: composition ambiguous plus price missing | 4 |
| Partial: composition missing | 14 |
| Partial: price missing only | 3 |
| Additional page-read attempts denied by budget | 22 |
| Scoring validation errors | 24 |

Pipeline errors and final-recommendation failures have different denominators: of 14 non-product extraction errors, one still appears in the final recommendations; three more final non-products are category URLs. Eight pipeline 404s correspond to two still-recommended entries.

## Interpretation

The new B2 fixes execution coverage (20/20) and is fast (6.21 s mean), but supplied links are overwhelmingly non-product destinations (53/57). QuickShop retains more traceable product-level evidence, while still exhibiting fallback fabrication risk, dead links and evidence-to-scoring overrides. B1 remains dominated by category/editorial entries. Neither the weak merchant heuristic nor unequal native evidence logging justifies a blanket safety/quality win.

This is a mixed-source comparison. No live availability, authenticity, seller safety, redirect destinations or full fit/stock/shipping audit was performed. Original run JSON and application code remain unchanged.
