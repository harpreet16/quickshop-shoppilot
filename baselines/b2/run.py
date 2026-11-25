import argparse
import os
import sys

from dotenv import load_dotenv

here = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(here, ".env"))
load_dotenv(os.path.join(here, "..", "..", ".env"))

PROVIDER = (os.getenv("WEBSEARCH_PROVIDER") or "openrouter").strip().lower()
MODEL = os.getenv("WEBSEARCH_MODEL") or {
    "openrouter": "google/gemini-3.8-flash",
    "gemini": "gemini-3.8-flash",
    "openai": "gpt-4o",
}.get(PROVIDER, "")


class BaselineError(RuntimeError):
    """An actionable baseline failure safe to include in evaluation results."""


def read_query(path):
    with open(path, "r") as f:
        return f.read().strip()


PROMPT = """You are a shopping assistant with live web access. For the request below,
search the web and recommend about three clothing products. For each, give the product name,
price, merchant, a link, and brief notes on price, quality (material/durability), and seller
legitimacy. Prefer majority natural-fiber garments and trustworthy sellers. If nothing
trustworthy fits the budget, say so rather than recommending a risky seller.

REQUEST:
{query}
"""


def web_grounded_call(query, mock=False):
    if mock:
        return (
            "[MOCK OUTPUT] No API call was made.\n"
            "A web-grounded model would return ~3 recommendations gathered from its own live\n"
            "web search (name, price, merchant, link, and short price/quality/legitimacy notes),\n"
            "with no team-built tools, triage, or deterministic scoring in between.\n"
        )

    prompt = PROMPT.format(query=query)

    if PROVIDER == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise BaselineError(
                "OPENROUTER_API_KEY not set. Add it to .env or baselines/b2/.env"
            )
        from openai import OpenAI

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=90.0,
            max_retries=0,
        )
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"plugins": [{"id": "web", "engine": "native"}]},
        )
        text = response.choices[0].message.content if response.choices else None
        if not text or not text.strip():
            raise BaselineError(
                "OpenRouter returned no text (blocked or empty response)"
            )
        return text

    if PROVIDER == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise BaselineError(
                "GEMINI_API_KEY not set. Add it to .env or baselines/b2/.env"
            )
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise BaselineError(
                "Missing google-genai. Install with: python -m pip install -e '.[eval]'"
            ) from None

        client = genai.Client(
            api_key=api_key, http_options=types.HttpOptions(timeout=90_000)
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
            ),
        )

        if not response.text or not response.text.strip():
            raise BaselineError("Gemini returned no text (blocked or empty response)")
        return response.text

    if PROVIDER == "openai":
        api_key = os.getenv("WEBSEARCH_API_KEY")
        if not api_key:
            raise BaselineError("WEBSEARCH_API_KEY not set for the OpenAI provider")
        from openai import OpenAI

        client = OpenAI(api_key=api_key, timeout=90.0, max_retries=0)
        resp = client.responses.create(
            model=MODEL,
            tools=[{"type": "web_search"}],
            input=prompt,
        )
        if not resp.output_text or not resp.output_text.strip():
            raise BaselineError("OpenAI returned no text (blocked or empty response)")
        return resp.output_text

    raise BaselineError("WEBSEARCH_PROVIDER must be 'openrouter', 'gemini' or 'openai'")


def main():
    parser = argparse.ArgumentParser(description="QuickShop B2 baseline")
    parser.add_argument(
        "--mock", action="store_true", help="Run offline, no key needed."
    )
    args = parser.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    query = read_query(os.path.join(here, "input.txt"))

    try:
        result = web_grounded_call(query, mock=args.mock)
    except BaselineError as exc:
        print(f"B2: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        # Provider exception bodies may include credentials; retain only type/status.
        code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
        hints = {
            400: "check model/tool compatibility and request parameters",
            401: "check the provider API key",
            402: "insufficient provider credits; check OpenRouter billing",
            403: "check API key permissions and project access",
            404: "check WEBSEARCH_MODEL availability for this API key",
            429: "provider quota/rate limit exhausted; check billing or retry later",
        }
        status = f" HTTP {code}" if isinstance(code, int) else ""
        hint = hints.get(code, "check provider availability and configuration")
        print(f"B2: {type(exc).__name__}{status}; {hint}", file=sys.stderr)
        return 1

    out_path = os.path.join(here, "output.txt")
    with open(out_path, "w") as f:
        f.write(result)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
