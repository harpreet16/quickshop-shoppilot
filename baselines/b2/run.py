import argparse
import os
import sys

from dotenv import load_dotenv

here = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(here, ".env"))
load_dotenv(os.path.join(here, "..", "..", ".env"))

PROVIDER = os.getenv("WEBSEARCH_PROVIDER", "gemini")
MODEL = os.getenv("WEBSEARCH_MODEL", "gemini-3.8-flash")


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

    if PROVIDER == "gemini":
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set. Add it to .env or baselines/b2/.env"
            )

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
            ),
        )

        return response.text

    if PROVIDER == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("WEBSEARCH_API_KEY"))
        resp = client.responses.create(
            model=MODEL,
            tools=[{"type": "web_search"}],
            input=prompt,
        )
        return resp.output_text

    raise ValueError(
        f"Unsupported WEBSEARCH_PROVIDER={PROVIDER!r}. Supported: 'gemini', 'openai'."
    )


def main():
    parser = argparse.ArgumentParser(description="QuickShop B2 baseline")
    parser.add_argument(
        "--mock", action="store_true", help="Run offline, no key needed."
    )
    args = parser.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    query = read_query(os.path.join(here, "input.txt"))

    result = web_grounded_call(query, mock=args.mock)

    out_path = os.path.join(here, "output.txt")
    with open(out_path, "w") as f:
        f.write(result)
    print(result)
    print(f"\nresult written in {out_path}")


if __name__ == "__main__":
    main()
