# Recommendation eligibility and failure audit

Source: `eval_20261122_190556.json`. All recommendation ranks from successful executions only: 108 entries, not 108 unique products across queries. Failed executions (26) and abstentions are tracked separately and do not contribute fake product failures. No live searches, page reads, redirect resolution, or paid API calls were performed.

Companions: `eligibility_audit_eval_20261122_190556.csv` (108 per-recommendation rows) and `.json` (same rows plus page evidence, fresh heuristic signals, and summaries).

## Method

- Extract recommendations in final-answer order; exclude rejected sections, suggestions for next steps, and stale text from failed executions. Totals checked against the prior manual inventory: QuickShop 48, B0 3, B1 42, B2 15.
- Review titles/URLs/reasons for product identity. Mark category and editorial recommendations as non-products; a saved 'not a product page' extraction is an additional flag, not independently verified truth. One generic B1 Amazon '100% Silk Blouse' entry stays unknown rather than being forced into a category.
- For product-like entries with an identifiable named merchant, call current `quickshop.tools.merchant.check_merchant`, then `quickshop.tools.scoring._score_legitimacy`; threshold >=3. Use actual hostname where available. Do not treat a Google grounding redirect as the seller domain. Merchant names in baseline prose are claims, not authenticated identities.
- Exclude non-products before the gate. B0's illustrative sellers are not real assessable merchants. Missing links can be supplemented only from the same QuickShop item's recorded score log and are still flagged as missing from the final answer.
- Check recorded page evidence for material/price agreement. Baselines do not save comparable page-evidence logs; absence is an evidence gap, not proof that their claims are false.

## Seller-gate results

| Measure | QuickShop | B0 | B1 | B2 |
|---|---:|---:|---:|---:|
| Recommendations assessed | 48 | 3 | 42 | 15 |
| Product-like entries passing the current heuristic gate | 44 | 0 | 0 | 8 |
| Product-like entries rejected by the gate (NOT proven unsafe) | 0 | 0 | 1 | 7 |
| Gate not applicable: non-product recommendation | 4 | 0 | 40 | 0 |
| Gate not assessable: synthetic/unclear identity | 0 | 3 | 1 | 0 |

QuickShop's 44 passes differ from its original 48 eligible score outputs because four recommendations are excluded as non-products before rescoring. The gate is not an independent safety oracle.

## Mutually exclusive primary outcomes

Priority: non-product -> not assessable -> merchant gate rejected -> other flagged issues -> no issue found by this limited offline checklist. Each column sums to the recommendation total.

| Measure | QuickShop | B0 | B1 | B2 |
|---|---:|---:|---:|---:|
| Not a product | 4 | 0 | 40 | 0 |
| Merchant gate rejected ('unsafe' proxy only) | 0 | 0 | 1 | 7 |
| Not assessable | 0 | 3 | 1 | 0 |
| Other failures / evidence gaps | 28 | 0 | 0 | 8 |
| No flagged issue in this limited offline screen | 16 | 0 | 0 | 0 |
| Total | 48 | 3 | 42 | 15 |

'Other failures' includes unknown evidence, not only established errors. QuickShop's 16 unflagged entries are not certified correct or safe; fit, stock, shipping and live authenticity were not exhaustively checked. Baseline zeros in that row cannot support a fair end-to-end quality ranking because only QuickShop saved native page evidence.

## Common failure tags (overlapping)

An entry can have several tags; these rows MUST NOT be summed.

| Measure | QuickShop | B0 | B1 | B2 |
|---|---:|---:|---:|---:|
| Not a product: category/editorial/extractor rejection | 4 | 0 | 40 | 0 |
| Unclear product identity | 0 | 0 | 1 | 0 |
| Illustrative catalog, not an assessable real seller | 0 | 3 | 0 | 0 |
| Merchant gate rejected (not confirmed unsafe) | 0 | 0 | 1 | 7 |
| No product link in final answer | 7 | 3 | 42 | 0 |
| Grounding redirect not resolved | 0 | 0 | 0 | 6 |
| No displayed numeric product price | 0 | 0 | 42 | 0 |
| Displayed price only approximate / a range | 0 | 0 | 0 | 8 |
| No matching usable saved page record | 11 | 3 | 42 | 15 |
| No structured saved natural-fiber share >=50% | 20 | 3 | 42 | 15 |
| No matching exact USD price in saved page evidence | 15 | 3 | 42 | 15 |
| Scoring fiber share conflicts with saved structured value | 2 | 0 | 0 | 0 |
| EUR-to-USD conversion without recorded rate | 2 | 0 | 0 | 0 |
| Recommended URL's saved read returned HTTP 404 | 2 | 0 | 0 | 0 |
| Explicit requested-size mismatch in recommended URL | 1 | 0 | 0 | 0 |
| Ethical-sourcing requirement not substantiated | 2 | 0 | 0 | 0 |
| Incidental substring counted as known brand | 1 | 0 | 0 | 0 |

## Representative findings

- **QuickShop non-products (4):** d2q14 #1 Walmart category; d2q15 #1 Levi's filter/category; d2q20 #3 Macy's category; d2q3 #4 J.Crew saved extraction explicitly returned 'not a product page'. The last is an extractor finding, not proof the URL can never be a product.
- **B1 non-products (40):** category/filter/editorial recommendations. d2q7 #3 is the only clearly named individual item (Naadam scarf), but no link or price is saved; the current merchant heuristic rejects Naadam. d2q25 #1 remains ambiguous.
- **Missing links:** seven QuickShop recommendations omit a product URL in their final answer (all three d2q7 scarves, both d2q11 coats, both d2q13 coats). Their URLs are recoverable only from tool logs. B0 and B1 omit all product links.
- **404s:** QuickShop d2q3 #5 Everlane oxford and d2q5 #3 Everlane tunic have saved HTTP 404 results yet are recommended.
- **Material conflicts:** QuickShop d2q2 #3 Gap tee and d2q8 #1 Banana Republic merino have structured fiber share 0 but scoring inputs claim 100. Raw text suggests parser limitations, so these are consistency failures, not proof the garments are synthetic.
- **Size mismatch:** d2q23 #2 Target link specifies 2X while the saved clarification answer is L.

## Why the 'unsafe' count is misleading

B2's seven rejected entries are Lands' End (3 recommendations), Dockers, Los Angeles Apparel, L.L.Bean and Huckberry. The current allowlist does not recognize these names; the helper then supplies unknown review/domain information and no return-policy signal. Rejection does not establish that any of them is unsafe.

The reverse problem also exists: **Dalle Piane Cashmere passes because `hm` occurs inside 'cashmere'**, accidentally matching the H&M alias. The helper consequently manufactures the known-brand defaults (10,000 external reviews and a return policy). This is one observed false brand-recognition match, not an exhaustive test of the matcher.

Confirmed unsafe sellers: **not established by this analysis**. Do not relabel heuristic rejections as scam detections. No brand-list or scoring code was changed to improve the reported counts.

## Separate QuickShop pipeline failures (all candidates, not just recommendations)

| Event / record type | Count |
|---|---:|
| Returned page records | 100 |
| OK page records | 36 |
| Partial page records | 41 |
| Unavailable page records | 23 |
| Unavailable: not a product page | 14 |
| Unavailable: HTTP 404 | 8 |
| Unavailable: HTTP 500 after four tries | 1 |
| Partial: composition ambiguous only | 20 |
| Partial: composition ambiguous plus price missing | 4 |
| Partial: composition missing | 14 |
| Partial: price missing only | 3 |
| Additional page-read attempts denied by five-page budget | 22 |
| Scoring validation-error events | 24 |

The 14 pipeline 'not a product page' errors are NOT 14 bad final recommendations. Only one of those extractor rejections corresponds to an item still recommended; three additional final non-products are identified from category URLs. Similarly, pipeline 404s (8) and recommended-item 404s (2) have different denominators.

## Interpretation

QuickShop produces more actionable, traceable individual recommendations than B1 in this artifact, but unsupported fallback claims, category leakage, dead links and evidence-to-scoring overrides remain. B2's apparent seller-gate disadvantage mainly exposes the allowlist's blind spots. To compare real safety/quality, independently verify the same product/seller facts for every system, keep unknowns explicit, and correct merchant matching rather than awarding points for reproducing its errors.

No live availability, authenticity, seller safety or redirect destinations were checked. Product/non-product labels were manually reviewed from the saved artifact. Source JSON and application code remain unchanged.
