"""
StreamingHook — pushes AfterToolCall events into an asyncio Queue from the agent thread,
so the SSE generator can forward them to the browser in real time.
"""
import asyncio

from strands.hooks import AfterToolCallEvent, HookProvider


class StreamingHook(HookProvider):
    def __init__(self, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self._queue = queue
        self._loop = loop
        self.calls: list[dict] = []

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(AfterToolCallEvent, self._on_tool_call)

    def _on_tool_call(self, event: AfterToolCallEvent):
        result = event.result
        status = result.get("status", "success") if isinstance(result, dict) else "success"
        call = {
            "tool": event.tool_use["name"],
            "status": status,
            "blocked": event.cancel_message is not None,
        }
        self.calls.append(call)
        # thread-safe push into the asyncio queue
        self._loop.call_soon_threadsafe(self._queue.put_nowait, {"event": "tool_call", "data": call})
