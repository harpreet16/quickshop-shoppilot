from typing import Literal


def render_recommendation(
    rank: int,
    title: str,
    price: float,
    merchant: str,
    url: str,
    scores: dict,
    evidence: list[str],
) -> str:
    """Render a single recommended product."""
    lines = []
    lines.append(f"{rank}. {title}")
    lines.append(f"   Price: ${price:.2f} from {merchant}")
    lines.append(f"   Link: {url}")
    lines.append(
        f"   Scores: price={scores['price']}/5, quality={scores['quality']}/5, legitimacy={scores['legitimacy']}/5"
    )
    lines.append(f"   Overall: {scores['overall']}/5 — Risk: {scores['risk']}")

    if evidence:
        lines.append("   Evidence:")
        for e in evidence[:5]:
            lines.append(f"     • {e}")

    return "\n".join(lines)


def render_warning(
    title: str,
    price: float,
    merchant: str,
    reason: str,
) -> str:
    """Render a product in the warning section."""
    return f"   ⚠ {title} (${price:.2f} from {merchant})\n     Reason: {reason}"


def render_report(
    query: str,
    recommendations: list[dict],
    warnings: list[dict] = None,
    abstain_message: str = None,
    tool_calls: int = None,
) -> str:
    """
    Render the full QuickShop report.

    Args:
        query: The user's original query
        recommendations: List of recommended products with scores
        warnings: List of products that failed the legitimacy gate
        abstain_message: If set, agent chose to abstain
        tool_calls: Number of tool calls made

    Returns:
        Formatted report string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("QuickShop Recommendations")
    lines.append("=" * 60)
    lines.append(f"\nQuery: {query}\n")

    if abstain_message:
        lines.append("ABSTAINED")
        lines.append(f"   {abstain_message}")
        lines.append("")
        lines.append("QuickShop could not find safe options matching your request.")
        lines.append("Consider:")
        lines.append("   • Increasing your budget")
        lines.append("   • Broadening your search")
        lines.append("   • Trying a different category")

    elif recommendations:
        lines.append(f"Top {len(recommendations)} Recommendations:\n")

        for i, rec in enumerate(recommendations, 1):
            lines.append(
                render_recommendation(
                    rank=i,
                    title=rec.get("title", "Unknown"),
                    price=rec.get("price", 0),
                    merchant=rec.get("merchant", "Unknown"),
                    url=rec.get("url", ""),
                    scores={
                        "price": rec.get("price_score", "?"),
                        "quality": rec.get("quality_score", "?"),
                        "legitimacy": rec.get("legitimacy_score", "?"),
                        "overall": rec.get("overall_score", "?"),
                        "risk": rec.get("risk", "unknown"),
                    },
                    evidence=rec.get("evidence", []),
                )
            )
            lines.append("")

    else:
        lines.append("No recommendations found.")

    if warnings:
        lines.append("-" * 60)
        lines.append("Not Recommended (failed legitimacy check):\n")
        for w in warnings:
            lines.append(
                render_warning(
                    title=w.get("title", "Unknown"),
                    price=w.get("price", 0),
                    merchant=w.get("merchant", "Unknown"),
                    reason=w.get("reason", "Failed legitimacy gate"),
                )
            )
        lines.append("")

    lines.append("-" * 60)
    if tool_calls is not None:
        lines.append(f"Tool calls: {tool_calls}")
    lines.append("Note: Scores are based on available evidence. Always verify")
    lines.append("before purchasing. QuickShop does not guarantee seller safety.")
    lines.append("=" * 60)

    return "\n".join(lines)


def render_risk_band(risk: Literal["low", "medium", "high"]) -> str:
    """Render a visual risk indicator."""
    if risk == "low":
        return "🟢 Low Risk"
    elif risk == "medium":
        return "🟡 Medium Risk"
    else:
        return "🔴 High Risk"
