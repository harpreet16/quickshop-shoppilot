# B2: Web-grounded single-call baseline

## Gemini through OpenRouter (default)

From the repository root, activate the project environment and install QuickShop:

```bash
source .venv/bin/activate
python -m pip install -e .
```

Add these values to the root `.env` (or `baselines/b2/.env`):

```dotenv
OPENROUTER_API_KEY=your-key-here
WEBSEARCH_PROVIDER=openrouter
WEBSEARCH_MODEL=google/gemini-3.8-flash
```

Enter the key locally, not in chat or shell history. No `GEMINI_API_KEY` is needed
for this mode. Exported variables override the B2 `.env`, which overrides the
root `.env`; update old provider/model overrides when switching providers.

B2 calls OpenRouter's OpenAI-compatible Chat Completions endpoint with the `web`
plugin and `engine=native`, enabling Gemini's native Google Search grounding.
It does not call Firecrawl or require a Google API key. Model tokens and native
search are billed to the OpenRouter account. Use a Google Gemini model supporting
native search; an arbitrary non-search model is not a grounded B2 replacement.

```bash
python baselines/b2/run.py --mock  # offline wiring check
# One live smoke query first:
python -m eval.runner --dataset 2 --systems b2 --queries d2q7
# Then all 20 B2 queries, saved as a new results file:
python -m eval.runner --dataset 2 --systems b2
```

The live commands spend provider credits. Existing evaluation JSON is not repaired
or overwritten. `--resume` skips queries already present, including failures;
use `--queries` in a fresh run to retry particular failures.

## Other providers

- Direct Google: install `python -m pip install -e '.[eval]'`, set
  `WEBSEARCH_PROVIDER=gemini`, `WEBSEARCH_MODEL=gemini-3.8-flash`, and `GEMINI_API_KEY`.
- Direct OpenAI: set `WEBSEARCH_PROVIDER=openai`, `WEBSEARCH_MODEL=gpt-4o`,
  and `WEBSEARCH_API_KEY`.
- Standalone B2 installation: `python -m pip install -r baselines/b2/requirements.txt`.

Success prints the answer and writes `baselines/b2/output.txt`. Missing SDKs/keys,
empty answers, and provider errors exit nonzero. Provider diagnostics contain the
error type and HTTP status, not raw response bodies or credentials. The eval runner
only accepts fresh stdout and records `error`/`exit_code`; it does not reuse stale
output files after failures. HTTP 402 indicates insufficient OpenRouter credits.

The historical run's stderr was not saved, so its exact failure cause cannot be
recovered. A missing `google-genai` SDK was reproduced for the old direct-Google
configuration. Offline regression coverage: `python -m pytest tests/test_b2.py`.
