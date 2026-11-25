# QuickShop

An agentic AI shopping assistant for clothing. Given a natural-language request, QuickShop
searches across retailers, gathers evidence on each candidate, and returns a short ranked
shortlist scored on three axes : **price**, **quality** (natural-fiber content), and **seller
legitimacy** : with the evidence behind every recommendation.

## Architecture

![QuickShop agentic system architecture](docs/architecture.jpg)

QuickShop is built as a single **orchestrating agent** (Strands harness, `gpt-oss-120b` via the
ASU Research Computing gateway) with a small set of typed tools and deterministic scoring. The
agent's job is not just to answer, but to decide *how* to answer : which is what makes the task
agentic rather than a single model call or a fixed pipeline.

### The agent's four decisions (its "agency")

1. **Clarify?** : Is the request specified well enough to search, or should it ask the user a
   question first (and which question yields the most for the fewest asks)?
2. **Search again?** : Are there enough good candidates, or should it widen/reword and search
   again? The agent decides when to stop looking.
3. **Which candidates to extract?** : Deep extraction costs API credits, so it picks only the
   candidates worth paying to investigate under the remaining budget.
4. **Abstain?** : Can it answer honestly, or is the correct response "no safe match" / "nothing
   in budget : raise it?" Choosing *not* to recommend is a first-class safety decision.

### Pipeline (input → output)

| Stage | What happens |
|-------|--------------|
| **1. Intake** | Check the request against required specs; ask clarifying questions if anything is missing. |
| **2. Discovery** | Call `search_listings` one or more times, widening until the candidate pool is sufficient. |
| **3. Triage** | Rank the pool on cheap listing-level signals; select which candidates justify expensive extraction under the budget. |
| **4. Evidence Extraction** | Parallel subagents (one per candidate, each from a fresh baseline) gather evidence via `fetch_product_evidence` and `check_merchant`. |
| **5. Scoring** | Deterministic Python scores each axis 1–5, applies the legitimacy gate, then ranks eligible candidates with a weighted geometric mean. |
| **6. Report** | Render the ranked shortlist (3–5) with evidence, a flagged higher-risk section, the rejection list, and a risk band. |

### Setup Instructions
```bash
# Clone and setup
git clone https://github.com/harpreet16/quickshop-shoppilot.git
cd quickshop-shoppilot
python -m venv .venv && source .venv/bin/activate
pip install -e '.[eval]'  # includes B2's Google GenAI SDK
cp .env.example .env  # Add: API_KEY, FIRECRAWL_API_KEY, OPENROUTER_API_KEY (B2)

# Run QuickShop agent (interactive, output to terminal)
python -m quickshop 'black jeans under $80'

# Use single quotes, or zsh turns "$80" into "0".
# Run it again with the same results and no API calls (--frozen).
# Run the query once without --frozen first, so there is something saved.
python -m quickshop --frozen 'black jeans under $80'
python -m eval.runner --systems quickshop --frozen

# Turn the newest results file in eval/results/ into a results table (also saved as a .md file)
python -m eval.metrics

# Run baselines (output written to baselines/b*/output.txt)
python baselines/b0/run.py
python baselines/b1/run.py
python baselines/b2/run.py

# Run tests
pytest tests/
# Pre-captured outputs are in outputs/ folder:
#   outputs/quickshop_output.txt  - Main agent output
#   outputs/b0_output.txt         - B0 baseline
#   outputs/b1_output.txt         - B1 baseline
#   outputs/b2_output.txt         - B2 baseline
```

### Browser UI (local pilot)

```bash
source .venv/bin/activate
pip install -e '.[ui]'
streamlit run app.py
# Or start with the Frozen toggle enabled:
streamlit run app.py -- --frozen
```

Open http://127.0.0.1:8501. Project configuration binds the server to localhost;
this pilot has no authentication and must not be exposed publicly.

Live mode uses server-side `.env` keys: `API_KEY` (ASU gateway)
and `FIRECRAWL_API_KEY` (search and product-page reading).
No keys are entered or displayed in the page. Gemini is not needed for this UI.
Keep `QUICKSHOP_EVIDENCE_REPLAY=0` for fresh live evidence.

Try: **black straight-leg jeans, size 32 waist, under $80**. Reply to clarification
questions in the chat box; the same agent invocation continues. Follow-up requests
reuse the conversation. Session controls stay on the left, replies and questions in
center chat, and live tool/result cards in the right column. Activity cards show
running/completed calls with expandable inputs and outputs, category colors and
risk indicators; rejected products appear in red. Cards use tool results, not parsed AI prose.
Use **Hide live activity** in the sidebar to expand chat to full width; **Show live activity**
restores the right column without interrupting ongoing work. Tables grow naturally inside
the chat feed, which handles scrolling; neither table has its own scrollbar.
The **Options** table below the events table lists discovered products with brand,
wrapped title, a small product-link pill, and the current verdict. Brands come only
from explicit tool data (otherwise `—`); products remain unreviewed or awaiting a
verdict until assessed. Rejections appear in red.
A compact table inside the main chat feed summarizes the ten latest events (for example,
"Editorialist — Unrecognized seller"). Conversation and activity feeds auto-scroll
to new content; activity is chronological. Evidence and raw tool payloads stay
collapsed until expanded. The UI extra requires Streamlit 1.67+ for native auto-scroll.
Merchant signals remain heuristics, not verified seller safety. Unscored candidates
are not promoted into recommendation cards.

**Frozen mode** uses synthetic fixed black-jeans listings/evidence inspired by
`outputs/quickshop_output.txt`, including an untrusted eBay seller. It still uses
the live ASU model and requires `API_KEY`, but makes no Firecrawl calls.
Demo links are placeholders, not purchasable offers. Other searches still receive
the same demo products. Mode changes and **New conversation** clear the browser's
conversation; they are disabled while work is active. Answer pending questions
within five minutes. Closing the browser does not cancel an in-flight API request.

The sidebar page-read counter resets per shopping turn and counts evidence tool
calls (including cache hits), not provider billing credits. Activity refreshes every
half second as tools start and finish. Search/model spending is not capped by this counter.

Offline UI tests: install `pip install -e '.[dev,ui]'`, then run
`pytest tests/test_web.py`. No paid API calls are required by these tests.
### Evaluation (results tables)

Compare QuickShop with the three baselines on the benchmark queries in `eval/benchmark.py`.

```bash
# 1. Run every system on every query, live, once. Results go to eval/results/eval_<date>.json
python -m eval.runner

# Only some systems, some queries, or one category:
python -m eval.runner --systems quickshop b1 --queries q1 q6
python -m eval.runner --category trust
python -m eval.runner --list            # show all benchmark queries

# 2. Run QuickShop again on the same saved data, to check the results repeat (no API calls)
python -m eval.runner --systems quickshop --frozen

# 3. Make the results table from the newest results file (or name the files you want)
python -m eval.metrics
python -m eval.metrics eval/results/eval_20261122_140000.json
```

`eval.metrics` prints two tables and saves them as `eval/results/metrics_<results file>.md`:

- **Summary:** one column per system. Risky sellers in the top 3, sellers blocked by the
  legitimacy gate, fabric verified from the product page, picks within budget, items
  recommended, tool calls, page reads, Firecrawl credits and seconds per query.
- **Per query:** one row per query and system, for checking the numbers by hand.

Good to know:

- QuickShop's numbers come from its real tool results, which the runner saves. Results files
  made before this was added have no tool log, so run the evaluation again.
- B0 and B1 numbers are read from their output text. B2 describes sellers in words, so its
  risky-seller column says "check by hand".
- "Fabric verified" only counts fabric read from the product page. The baselines never read
  pages, so theirs is always 0.
- Run each query live only once. A second live run replaces the saved searches, and the
  results will no longer match.

### Scoring (the key design decision)

The LLM **extracts** evidence into a schema but does **not** compute the scores : scoring is
deterministic Python over that evidence, so results are reproducible and auditable.

- **Per-axis scores (1–5):** price · quality (natural-fiber percentage) · legitimacy.
- **Legitimacy gate:** any candidate below the trust threshold is ineligible regardless of price
  or quality, and is shown separately with a warning. *A good price cannot offset a bad seller.*
- **Weighted geometric mean:** ranks the eligible candidates, penalizing a weak axis harder than
  a plain average would.

This replaces the baseline's arithmetic averaging, under which a cheap, nice-looking item from an
untrustworthy seller could still reach the shortlist.

### Memory

- **Session State** : clarified query, candidates, evidence, and scores across turns, so a
  follow-up like "anything cheaper?" re-ranks the existing pool instead of restarting.
- **Evidence Cache** : validated records keyed by URL with a freshness TTL. Replaces the manual
  `products.json` of the baseline and makes evaluation reproducible.

### Typed tools

All tools return schema-validated results and can report an explicit `unavailable` state instead
of guessing.

| Tool | Returns | Source |
|------|---------|--------|
| `search_listings` | candidate listings | Firecrawl web search |
| `fetch_product_evidence` | evidence record (composition, origin, policy, reviews) | Firecrawl |
| `check_merchant` | merchant signals (domain age, reviews, allowlist) | local brand/domain heuristics (no live search) |
| `score_product` | per-axis scores | deterministic Python |
| `ask_user` | clarification answers | user |

### External services

- **Firecrawl Search** : web discovery with direct URLs; price, rating and reviews remain null until verified from page evidence. B1 also uses this search without page reads, so its metadata is sparse.
- **Firecrawl** : schema-constrained JSON extracted from a product page for evidence.

**Search migration:** Live QuickShop and B1 need only `FIRECRAWL_API_KEY` for discovery;
remove the old search-provider key from your local environment if no longer needed.
`/health.services` now contains `firecrawl` and `model` only. Saved search snapshots remain
replayable, including older shopping results. B1's offline fixture and captured evaluation
outputs are historical; rerun live evaluations before comparing the new search provider.
B2 deliberately retains model-native Google/OpenAI search as a separate benchmark.
Search does not scrape pages; product facts and photos require the existing evidence step.
## Product evidence (`fetch_product_evidence`)

Given a product URL, `quickshop/evidence/` returns one validated `EvidenceRecord`. It does no search,
no merchant checks and no 1 to 5 scoring: it only reads a page and reports what it found.

```
URL -> canonicalize -> cache (per-field TTL) -> Firecrawl (JSON extraction + markdown)
    -> deterministic fabric parser -> EvidenceRecord -> cache -> dict
```

| File | Job |
|------|-----|
| `schema.py` | `EvidenceRecord` and its parts. Unknown is `None`, never 0. Percentages 0 to 100, currency is a code. |
| `firecrawl_client.py` | Product-page Firecrawl client. Never raises; failures become `status="unavailable"` with a reason. Exposes a calls/credits counter. |
| `fabric.py` + `fiber_config.py` | Pure-Python composition parser. Fiber names, categories and part labels live in `fiber_config.py` as data. |
| `cache.py` | SQLite cache keyed by canonical URL. `canonicalize_url()` lives here. |
| `service.py` | The pipeline (`EvidenceService`). `build_record()` is pure and testable. |
| `tool.py` | The Strands `@tool` the agent sees. Always returns a dict that validates against the schema. |

**The model extracts, Python parses.** Firecrawl copies the composition text verbatim. Python turns it
into fibers and percentages and computes `natural_fiber_pct` for the **main fabric only** (shell/body,
or the only part given). Lining, trim and filling are kept but never counted. If the extracted text
is not on the page, it is discarded rather than trusted.

**Status:** `ok` means composition was read unambiguously and a price was found. `partial` means
something is missing or ambiguous (see `error_reason` and `parse_notes`). `unavailable` means the page
could not be read. `composition_confidence` is `explicit`, `ambiguous` (e.g. percentages do not total
100, "approx.", ranges, several unlabeled fabrics; never rescaled) or `missing`.

**Config flags**

| Flag | Where | Default |
|------|-------|---------|
| `COUNT_REGENERATED_AS_NATURAL` (viscose/rayon, modal, lyocell, cupro...) | `fiber_config.py` | `False`. Always reported separately as `regenerated_fiber_pct`. |
| `SUM_TOLERANCE` for "totals about 100" | `fiber_config.py` | `1.0` |
| `FIELD_GROUPS`, `TTLS`, `NEGATIVE_TTL` | `cache.py` | composition/origin/brand 30 days, reviews 7 days, price/stock 6 hours, failures 15 minutes |
| `FIRECRAWL_API_KEY` | `.env` | empty. Without it the tool returns `unavailable`, it does not crash. |
| `QUICKSHOP_EVIDENCE_CACHE` | `.env` | `.cache/evidence.sqlite3` |
| `QUICKSHOP_EVIDENCE_REPLAY=1` | `.env` | off. Serve only from the cache, never call Firecrawl (reproducible evaluation). |
| `QUICKSHOP_SEARCH_SNAPSHOT` | `.env` | `.cache/search_snapshot.json`. Where saved searches are kept. |
| `QUICKSHOP_SEARCH_REPLAY=1` | `.env` | off. Use only saved searches, never call Firecrawl search. `--frozen` turns this on, along with `QUICKSHOP_EVIDENCE_REPLAY`. |

**Cost.** A fresh page read is about 5 Firecrawl credits (1 + 4 for JSON extraction). Cached reads are
free. For the budget hook, `quickshop.evidence.tool.get_usage()` returns combined search/page-read Firecrawl calls and reported credits
plus cache hits and misses. The cache can be frozen with `EvidenceCache.export_json()`.

**Tests:** `pytest` runs everything offline from saved page fixtures in `tests/evidence/fixtures/`.
The one live test is skipped unless you run
`FIRECRAWL_API_KEY=... QUICKSHOP_LIVE_URL=<product url> pytest --run-live`.
