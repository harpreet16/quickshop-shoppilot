import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from eval.benchmark import BENCHMARK_QUERIES, get_queries_by_category, get_query_by_id


def run_quickshop(query: str, timeout: int = 120) -> dict:
    from quickshop.agent.orchestrator import build_agent

    start = time.time()
    try:
        agent = build_agent(credits=5)
        result = agent(query)
        elapsed = time.time() - start

        return {
            "success": True,
            "output": str(result) if result else "[No output captured]",
            "tool_calls": len(agent.trace.calls),
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_seconds": round(time.time() - start, 2),
        }


def run_b0(query: str) -> dict:
    """Run B0 baseline (static products, LLM scoring)."""
    here = Path(__file__).parent.parent / "baselines" / "b0"

    (here / "input.txt").write_text(query)

    start = time.time()
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(here / "run.py")],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(here.parent.parent),
        )
        elapsed = time.time() - start

        output = (
            (here / "output.txt").read_text()
            if (here / "output.txt").exists()
            else result.stdout
        )

        return {
            "success": result.returncode == 0,
            "output": output,
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_seconds": round(time.time() - start, 2),
        }


def run_b1(query: str) -> dict:
    """B1 baseline (SerpAPI + LLM scoring, no page reads)."""
    here = Path(__file__).parent.parent / "baselines" / "b1"

    (here / "input.txt").write_text(query)

    start = time.time()
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(here / "run.py")],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(here.parent.parent),
        )
        elapsed = time.time() - start

        output = (
            (here / "output.txt").read_text()
            if (here / "output.txt").exists()
            else result.stdout
        )

        return {
            "success": result.returncode == 0,
            "output": output,
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_seconds": round(time.time() - start, 2),
        }


def run_b2(query: str) -> dict:
    """B2 baseline (Gemini with web grounding)."""
    here = Path(__file__).parent.parent / "baselines" / "b2"

    (here / "input.txt").write_text(query)

    start = time.time()
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(here / "run.py")],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(here.parent.parent),
        )
        elapsed = time.time() - start

        output = (
            (here / "output.txt").read_text()
            if (here / "output.txt").exists()
            else result.stdout
        )

        return {
            "success": result.returncode == 0,
            "output": output,
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_seconds": round(time.time() - start, 2),
        }


RUNNERS = {
    "quickshop": run_quickshop,
    "b0": run_b0,
    "b1": run_b1,
    "b2": run_b2,
}


def run_evaluation(
    systems: list[str] = None,
    queries: list[str] = None,
    category: str = None,
    output_dir: str = None,
) -> dict:
    """
    Run evaluation across systems and queries.

    Args:
        systems: List of systems to evaluate ["quickshop", "b0", "b1", "b2"]
        queries: List of query IDs to run, or None for all
        category: Filter queries by category
        output_dir: Directory to save results

    Returns:
        Evaluation results dict
    """
    if systems is None:
        systems = ["quickshop", "b0", "b1", "b2"]

    if queries:
        benchmark = [get_query_by_id(q) for q in queries if get_query_by_id(q)]
    elif category:
        benchmark = get_queries_by_category(category)
    else:
        benchmark = BENCHMARK_QUERIES

    results = {
        "timestamp": datetime.now().isoformat(),
        "systems": systems,
        "queries": [q["id"] for q in benchmark],
        "runs": [],
    }

    for query_info in benchmark:
        query_id = query_info["id"]
        query_text = query_info["query"]

        print(f"\n{'=' * 60}")
        print(f"Query {query_id}: {query_text}")
        print(f"Expected: {query_info['expected_behavior']}")
        print(f"{'=' * 60}")

        query_results = {
            "query_id": query_id,
            "query": query_text,
            "category": query_info["category"],
            "expected": query_info["expected_behavior"],
            "system_results": {},
        }

        for system in systems:
            print(f"\n  Running {system}...")
            runner = RUNNERS.get(system)
            if runner:
                result = runner(query_text)
                query_results["system_results"][system] = result
                status = "✓" if result["success"] else "✗"
                print(f"  {status} {system}: {result.get('elapsed_seconds', '?')}s")
                if not result["success"]:
                    print(f"    Error: {result.get('error', 'Unknown')}")
            else:
                print(f"  ✗ Unknown system: {system}")

        results["runs"].append(query_results)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"eval_{timestamp}.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="QuickShop Evaluation Runner")
    parser.add_argument(
        "--systems",
        "-s",
        nargs="+",
        default=["quickshop", "b0", "b1", "b2"],
        choices=["quickshop", "b0", "b1", "b2"],
        help="Systems to evaluate",
    )
    parser.add_argument(
        "--queries",
        "-q",
        nargs="+",
        help="Specific query IDs to run (e.g., q1 q2 q3)",
    )
    parser.add_argument(
        "--category",
        "-c",
        choices=["basic", "quality", "trust", "edge", "abstain"],
        help="Run only queries in this category",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="eval/results",
        help="Output directory for results",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available benchmark queries and exit",
    )

    args = parser.parse_args()

    if args.list:
        print("Available benchmark queries:")
        print("-" * 60)
        for q in BENCHMARK_QUERIES:
            print(f"  {q['id']:4} [{q['category']:8}] {q['query']}")
        return

    run_evaluation(
        systems=args.systems,
        queries=args.queries,
        category=args.category,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()
