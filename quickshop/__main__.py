# To run use: python -m quickshop "black jeans under $80"
# Add --frozen to reuse saved searches and saved page evidence, so the run makes no SerpAPI
# or Firecrawl calls and gives the same tool results every time.
import os
import sys

from quickshop.agent.orchestrator import build_agent


def use_frozen_mode():
    # both tools read these when they are first called
    os.environ["QUICKSHOP_SEARCH_REPLAY"] = "1"
    os.environ["QUICKSHOP_EVIDENCE_REPLAY"] = "1"


def main():
    args = sys.argv[1:]
    if "--frozen" in args:
        args = [a for a in args if a != "--frozen"]
        use_frozen_mode()
        print("Frozen mode: using saved searches and saved page evidence only.")
    agent = build_agent()
    request = " ".join(args) or input("What are you looking for? ").strip()
    # the agent keeps the chat in memory, so follow-ups can work
    while request:
        agent(request)
        print()
        request = input("Anything else? (press Enter to quit) ").strip()
    print(f"Tool calls this run: {len(agent.trace.calls)}")


if __name__ == "__main__":
    main()
