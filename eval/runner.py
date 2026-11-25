import argparse
import json
import os
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

# suppress known upstream Strands harness warnings that don't affect correctness
warnings.filterwarnings("ignore", message="Invalid configuration parameters.*api_key.*", category=UserWarning)
warnings.filterwarnings("ignore", message="context_window_limit is not set", category=UserWarning)
warnings.filterwarnings("ignore", message="prompt caching not applied", category=UserWarning)
# suppress the double-import warning caused by sys.path manipulation below
warnings.filterwarnings("ignore", message=".*found in sys.modules.*", category=RuntimeWarning)

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from eval.benchmark import BENCHMARK_QUERIES, get_queries_by_category, get_query_by_id
from eval.dataset2 import (
    DATASET2_QUERIES,
    get_queries_by_category as get_d2_queries_by_category,
    get_query_by_id as get_d2_query_by_id,
)


def _firecrawl_credits_used() -> int:
    # total Firecrawl credits spent so far in this process (0 if it cannot be read)
    try:
        from quickshop.evidence.tool import get_usage
        return int(get_usage()["firecrawl"]["credits_used"] or 0)
    except Exception:
        return 0


def run_quickshop(query: str, timeout: int = 120) -> dict:
    from quickshop.agent.orchestrator import build_agent
    from eval.recorder import ToolRecorder

    start = time.time()
    credits_before = _firecrawl_credits_used()
    try:
        agent = build_agent(credits=5)
        # keep every tool input and result, so eval/metrics.py can use the real scores
        recorder = ToolRecorder()
        agent.hooks.add_hook(recorder)
        result = agent(query)
        elapsed = time.time() - start

        return {
            "success": True,
            "output": str(result) if result else "[No output captured]",
            "tool_calls": len(agent.trace.calls),
            "elapsed_seconds": round(elapsed, 2),
            "firecrawl_credits": _firecrawl_credits_used() - credits_before,
            "tool_log": recorder.calls,
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
    """B1 baseline (Firecrawl search + LLM scoring, no page reads)."""
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

        # stdout belongs to this invocation; output.txt may be stale after a failure.
        success = result.returncode == 0 and bool(result.stdout.strip())
        outcome = {
            "success": success,
            "output": result.stdout.strip() if success else "",
            "elapsed_seconds": round(elapsed, 2),
            "exit_code": result.returncode,
        }
        if not success:
            outcome["error"] = result.stderr.strip()[-4000:] or (
                "B2 returned empty output" if result.returncode == 0
                else f"B2 exited with code {result.returncode}"
            )
        return outcome
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
    dataset: int = 1,
    from_id: str = None,
    resume: bool = False,
) -> dict:
    """
    Run evaluation across systems and queries.

    Saves results incrementally after every query so a crash only loses the
    query currently running. Use --resume to continue from where it stopped.

    Args:
        systems:    Systems to evaluate. Default: all four.
        queries:    Specific query IDs to run. Default: all in the dataset.
        category:   Filter by category instead of running all.
        output_dir: Where to write results JSON.
        dataset:    1 = original benchmark, 2 = Reddit-sourced dataset2.
        from_id:    Skip every query whose ID comes before this one.
        resume:     Load the latest results file and skip completed queries.
    """
    if systems is None:
        systems = ["quickshop", "b0", "b1", "b2"]

    if dataset == 2:
        all_queries = DATASET2_QUERIES
        _get_by_id = get_d2_query_by_id
        _get_by_category = get_d2_queries_by_category
    else:
        all_queries = BENCHMARK_QUERIES
        _get_by_id = get_query_by_id
        _get_by_category = get_queries_by_category

    if queries:
        benchmark = [_get_by_id(q) for q in queries if _get_by_id(q)]
    elif category:
        benchmark = _get_by_category(category)
    else:
        benchmark = all_queries

    # --from-id: skip everything before the given query
    if from_id:
        ids = [q["id"] for q in benchmark]
        if from_id not in ids:
            print(f"Warning: --from-id '{from_id}' not found. Running all queries.")
        else:
            cut = ids.index(from_id)
            if cut:
                print(f"Skipping {cut} queries before {from_id}: {ids[:cut]}")
            benchmark = benchmark[cut:]

    # --resume: load latest partial file and skip already-completed queries
    existing_results = None
    save_path = None

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        if resume:
            existing = sorted(Path(output_dir).glob("eval_*.json"))
            if existing:
                save_path = str(existing[-1])
                existing_results = json.loads(Path(save_path).read_text())
                done = {r["query_id"] for r in existing_results.get("runs", [])}
                before = len(benchmark)
                benchmark = [q for q in benchmark if q["id"] not in done]
                print(f"Resuming {Path(save_path).name}: "
                      f"{before - len(benchmark)} done, {len(benchmark)} remaining.")
            else:
                print("--resume: no results file found, starting fresh.")

        if not save_path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(output_dir, f"eval_{ts}.json")

        print(f"Saving incrementally to: {save_path}\n")

    results = existing_results or {
        "timestamp": datetime.now().isoformat(),
        "dataset": dataset,
        "systems": systems,
        "queries": [q["id"] for q in benchmark],
        "runs": [],
    }

    total = len(benchmark)
    for idx, query_info in enumerate(benchmark, 1):
        query_id   = query_info["id"]
        query_text = query_info["query"]

        print(f"\n{'=' * 60}")
        print(f"[{idx}/{total}] {query_id}: {query_text}")
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
            runner_fn = RUNNERS.get(system)
            if runner_fn:
                result = runner_fn(query_text)
                query_results["system_results"][system] = result
                status = "✓" if result["success"] else "✗"
                print(f"  {status} {system}: {result.get('elapsed_seconds', '?')}s")
                if not result["success"]:
                    print(f"    Error: {result.get('error', 'Unknown')}")
            else:
                print(f"  ✗ Unknown system: {system}")

        results["runs"].append(query_results)

        # Write after every query — a crash only loses the one in progress
        if save_path:
            with open(save_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"  💾 saved ({idx}/{total} queries done)")

    if save_path:
        print(f"\nAll done. Results in {save_path}")

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
    parser.add_argument(
        "--frozen",
        action="store_true",
        help="QuickShop uses saved searches and saved page evidence only (no Firecrawl calls)",
    )
    parser.add_argument(
        "--dataset", "-d",
        type=int, choices=[1, 2], default=1,
        help="1 = original benchmark (default), 2 = Reddit-sourced dataset",
    )
    parser.add_argument(
        "--from-id", dest="from_id",
        help="Skip all queries before this ID (e.g. --from-id d2q3)",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Load the latest results file and skip already-completed queries",
    )

    args = parser.parse_args()

    if args.frozen:
        from quickshop.__main__ import use_frozen_mode
        use_frozen_mode()

    if args.list:
        print("Available benchmark queries:")
        print("-" * 60)
        queries_to_list = DATASET2_QUERIES if args.dataset == 2 else BENCHMARK_QUERIES
        label = f"Dataset {args.dataset}"
        print(f"{label}:")
        for q in queries_to_list:
            src = f"  [{q.get('source','')}]" if args.dataset == 2 else ""
            print(f"  {q['id']:6} [{q['category']:8}] {q['query']}{src}")
        return

    run_evaluation(
        systems=args.systems,
        queries=args.queries,
        category=args.category,
        output_dir=args.output,
        dataset=args.dataset,
        from_id=getattr(args, "from_id", None),
        resume=getattr(args, "resume", False),
    )


if __name__ == "__main__":
    main()
