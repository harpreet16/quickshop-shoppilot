# Saves every tool call QuickShop makes, with its input and its result,
# so the metrics script can use the real scores instead of reading the final text.
import json

from strands.hooks import AfterToolCallEvent, HookProvider


def read_tool_output(result):
    """Turn a tool result back into the dict (or text) the tool returned."""
    parts = [block.get("text", "") for block in (result or {}).get("content", []) if isinstance(block, dict)]
    text = "".join(parts)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text


class ToolRecorder(HookProvider):
    def __init__(self):
        self.calls = []

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(AfterToolCallEvent, self.record)

    def record(self, event):
        self.calls.append({
            "tool": event.tool_use["name"],
            "input": event.tool_use.get("input") or {},
            "output": read_tool_output(event.result),
        })
