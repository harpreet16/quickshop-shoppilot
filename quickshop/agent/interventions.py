# These checks run before each tool call and can stop it.
# One limits the costly page reads. The other stops questions the user already answered.
import re

from strands.interventions import Deny, InterventionHandler, Proceed

COSTLY_TOOLS = {"fetch_product_evidence"}

class CreditBudget(InterventionHandler):
    name = "credit-budget"

    def __init__(self, credits=5):
        self.credits = credits
        self.used = 0

    def before_invocation(self, event, **kwargs):
        # a new user request starts with a full budget
        self.used = 0
        return Proceed()

    def before_tool_call(self, event, **kwargs):
        if event.tool_use["name"] not in COSTLY_TOOLS:
            return Proceed()
        if self.used >= self.credits:
            return Deny(reason=f"Budget used up ({self.credits} page reads). "
                               "Do not read more pages. Decide with the evidence you have.")
        self.used += 1
        return Proceed()


# Budget and size the user already wrote in their request, e.g. "size 32 waist, under $80"
_NUM = r"\$?\s*(\d+(?:\.\d{1,2})?)"
_BUDGET_PATTERNS = [
    re.compile(r"\b(?:under|below|less than|max(?:imum)?|up to|at most|no more than|budget(?: of| is)?)\s*" + _NUM, re.I),
    re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)\s*(?:or less|or under|and under|max)\b", re.I),
    re.compile(r"<=?\s*" + _NUM),
]
_DOLLAR = re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)")
_SIZE_PATTERNS = [
    re.compile(r"\bsize\s*:?\s*(\d{1,2}(?:\s*x\s*\d{1,2})?|xxs|xs|s|m|l|xl|xxl|xxxl|small|medium|large)\b", re.I),
    re.compile(r"\b(\d{2})\s*(?:inch\s*|in\s*|\"\s*)?waist\b", re.I),
    re.compile(r"\bwaist\s*:?\s*(\d{2})\b", re.I),
]
_ASKS_BUDGET = re.compile(r"budget|price|spend|cost|how much|\$", re.I)
_ASKS_SIZE = re.compile(r"\bsize\b|\bwaist\b", re.I)
_ASKS_OTHER_FIT = re.compile(r"inseam|length|height|tall", re.I)


def find_known_constraints(text):
    """Find the budget and size in the user's request. Anything not given is left out."""
    known = {}
    for pattern in _BUDGET_PATTERNS:
        match = pattern.search(text)
        if match:
            known["budget"] = float(match.group(1))
            break
    else:
        # a lone "$80" in a shopping request is a budget too
        match = _DOLLAR.search(text)
        if match:
            known["budget"] = float(match.group(1))
    for pattern in _SIZE_PATTERNS:
        match = pattern.search(text)
        if match:
            known["size"] = match.group(1)
            break
    return known


def _user_text(messages):
    parts = []
    for message in messages or []:
        if message.get("role") != "user":
            continue
        for block in message.get("content") or []:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
    return " ".join(parts)


class KnownConstraints(InterventionHandler):
    # Stops ask_user from asking for a budget or size the user already gave.
    # In our pilot the agent asked "What is your max budget?" for a query that said "under $80".
    name = "known-constraints"

    def __init__(self):
        self.known = {}

    def before_invocation(self, event, **kwargs):
        # follow-ups like "anything cheaper?" keep what was said before, new values replace old ones
        self.known.update(find_known_constraints(_user_text(getattr(event, "messages", None))))
        return Proceed()

    def before_tool_call(self, event, **kwargs):
        if event.tool_use["name"] != "ask_user":
            return Proceed()
        question = str((event.tool_use.get("input") or {}).get("question", ""))
        if "budget" in self.known and _ASKS_BUDGET.search(question):
            return Deny(reason=f"The user already gave a budget of ${self.known['budget']:g} in their "
                               "request. Do not ask again. Use it as the hard price limit.")
        if "size" in self.known and _ASKS_SIZE.search(question) and not _ASKS_OTHER_FIT.search(question):
            return Deny(reason=f"The user already gave their size ({self.known['size']}) in their "
                               "request. Do not ask again.")
        return Proceed()
