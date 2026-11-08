# QuickShop Evaluation Outputs

This folder contains real outputs from all systems for Milestone 2 comparison.

## Query Used
**"black straight-leg jeans, size 32 waist, under $80"**

## Output Files

| File | System | Description |
|------|--------|-------------|
| `quickshop_output.txt` | **QuickShop (Main Agent)** | Full agentic pipeline with tool calling, deterministic scoring, legitimacy gate |
| `b0_output.txt` | **B0 Baseline** | Static products.json + LLM scoring |
| `b1_output.txt` | **B1 Baseline** | SerpAPI search + LLM scoring (no page reads) |
| `b2_output.txt` | **B2 Baseline** | Gemini 3.8 with Google Search grounding |

## Key Differences

### QuickShop (27 tool calls)
- Asks clarifying questions
- Checks merchant trustworthiness before reading pages
- Fetches real product evidence (Firecrawl)
- **Deterministic scoring** - Python computes scores, not LLM
- **Legitimacy gate** - blocks items from untrusted sellers regardless of price
- Respects 5-page budget
- Abstains when composition unknown

### B0 (Static)
- Uses hardcoded product list
- LLM scores everything
- No real-time data

### B1 (SerpAPI + LLM)
- Real search results
- LLM scores from metadata only (no page reads)
- No composition verification

### B2 (Gemini Grounding)
- Single model call with web search
- No tool decomposition
- No deterministic scoring
- No legitimacy gate
