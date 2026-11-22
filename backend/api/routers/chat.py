"""
POST /chat — streams the agent's work as Server-Sent Events.

SSE event types the frontend will receive, in order:
  thinking   → agent started, show a loading indicator
  tool_call  → one tool finished (search, merchant check, page read, score, question)
  question   → agent wants to ask the user something; display it, let them reply in the next POST
  done       → final markdown response + session_id + usage stats
  error      → something went wrong; show an error state
"""
import asyncio
import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from strands import tool

from quickshop.agent.orchestrator import build_agent
from quickshop.evidence.tool import get_usage
from quickshop.tools import DEFAULT_TOOLS
from ..hooks import StreamingHook
from ..models import ChatRequest

router = APIRouter(tags=["chat"])

# One shared executor — the agent is CPU/IO-bound, 4 workers is plenty
_executor = ThreadPoolExecutor(max_workers=4)

# Thread-local so each request's ask_user pushes to its own SSE queue
_tl = threading.local()


@tool
def ask_user(question: str) -> str:
    """Ask the shopper a short clarifying question (e.g. their size or height).
    Ask one question at a time and only for what is strictly needed.

    Args:
        question: The question to show the shopper.

    Returns:
        The shopper's answer, or a note that there was no answer.
    """
    # Push the question into the SSE stream so the frontend can display it
    queue: asyncio.Queue | None = getattr(_tl, "queue", None)
    loop: asyncio.AbstractEventLoop | None = getattr(_tl, "loop", None)
    if queue is not None and loop is not None:
        loop.call_soon_threadsafe(
            queue.put_nowait,
            {"event": "question", "data": {"question": question}},
        )
    # For now, return no answer — the user can follow up in the next POST /chat
    return "No answer given. Continue without it and note that you will need it for a precise result."


# Replace stdin ask_user with the web version
_WEB_TOOLS = [t for t in DEFAULT_TOOLS if t.tool_name != "ask_user"] + [ask_user]


def _sse(event: str, payload: dict) -> dict:
    """Format one SSE event for sse-starlette."""
    return {"event": event, "data": json.dumps(payload)}


async def _agent_stream(query: str, session_id: str) -> AsyncGenerator[dict, None]:
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    streaming_hook = StreamingHook(queue, loop)

    yield _sse("thinking", {"message": "Finding the best options for you…"})

    def _run():
        # Wire this thread's ask_user to the SSE queue
        _tl.queue = queue
        _tl.loop = loop
        try:
            agent = build_agent(
                tools=_WEB_TOOLS,
                session_id=session_id,
                extra_hooks=[streaming_hook],
            )
            result = agent(query)
            response_text = str(result).strip()

            try:
                usage = get_usage()
                credits = usage.get("firecrawl", {}).get("credits_used", 0)
            except Exception:
                credits = 0

            loop.call_soon_threadsafe(
                queue.put_nowait,
                {
                    "event": "done",
                    "data": {
                        "response": response_text,
                        "session_id": session_id,
                        "tool_calls": len(streaming_hook.calls),
                        "firecrawl_credits": credits,
                    },
                },
            )
        except Exception as exc:
            loop.call_soon_threadsafe(
                queue.put_nowait,
                {"event": "error", "data": {"message": str(exc), "code": "AGENT_ERROR"}},
            )
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

    loop.run_in_executor(_executor, _run)

    while True:
        item = await queue.get()
        if item is None:
            break
        yield item


@router.post(
    "/chat",
    summary="Start or continue a shopping conversation",
    description=(
        "Streams the agent's progress as Server-Sent Events. "
        "Connect with `EventSource` or any SSE client. "
        "Pass back the `session_id` from the `done` event to continue the conversation."
    ),
)
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())
    return EventSourceResponse(_agent_stream(body.query, session_id))
