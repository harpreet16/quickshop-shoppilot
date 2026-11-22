# The file that calls the Strands harness.
from strands_harness import create_harness

from quickshop.agent.hooks import TraceLogger
from quickshop.agent.interventions import CreditBudget, KnownConstraints
from quickshop.agent.prompts import build_instructions
from quickshop.config import build_model
from quickshop.tools import DEFAULT_TOOLS


def build_agent(
    tools=None,
    credits=5,
    session_id=None,
    model=None,
    extra_hooks=None,
    instructions=None,
):
    # tools and model can be swapped. extra_hooks are appended after the TraceLogger.
    if tools is None:
        tools = DEFAULT_TOOLS
    if model is None:
        model = build_model()
    budget = CreditBudget(credits)
    constraints = KnownConstraints()
    trace = TraceLogger()
    hooks = [trace] + (list(extra_hooks) if extra_hooks else [])
    agent = create_harness(
        model=model,
        instructions=instructions
        if instructions is not None
        else build_instructions(credits),
        tools=tools,
        builtin_tools=[],  # set no shell, file or web tools
        builtin_plugins=[],
        skills=False,
        memory=False,
        background_tasks=False,
        # Sessions are saved to disk, and the user's size and height would be saved too.
        # It's off unless a session_id is given.
        session={"id": session_id, "dir": ".sessions"} if session_id else False,
        interventions=[budget, constraints],
        hooks=hooks,
    )
    # the caller can read the budget and the trace after a run
    agent.budget = budget
    agent.constraints = constraints
    agent.trace = trace
    return agent
