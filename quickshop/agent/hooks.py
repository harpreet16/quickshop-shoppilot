# A hook runs after something happens. This writes every tool call
# so our check can count them later.
from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent, HookProvider


class TraceLogger(HookProvider):
    def __init__(self):
        self.calls = []
        self.on_call = None
        self.on_start = None

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(BeforeToolCallEvent, self.started)
        registry.add_callback(AfterToolCallEvent, self.log)

    def started(self, event):
        if self.on_start is not None:
            self.on_start(
                {
                    "tool": event.tool_use["name"],
                    "input": event.tool_use["input"],
                    "tool_id": event.tool_use["toolUseId"],
                    "status": "running",
                }
            )

    def log(self, event):
        call = {
            "tool": event.tool_use["name"],
            "input": event.tool_use["input"],
            "status": event.result["status"],
            "blocked": event.cancel_message is not None,
        }
        self.calls.append(call)
        if self.on_call is not None:
            tool_id = event.tool_use.get("toolUseId")
            self.on_call(
                {**call, "result": event.result, **({"tool_id": tool_id} if tool_id else {})}
            )
