import math
from typing import Optional, Literal

from strands import tool

from quickshop.schemas import Scores

LEGITIMACY_GATE_THRESHOLD = 3

PRICE_BRACKETS = [
    (30, 5),
    (50, 4),
    (80, 3),
    (120, 2),
    (float("inf"), 1),
]

QUALITY_BRACKETS = [
    (90, 5),
    (70, 4),
    (50, 3),
    (30, 2),
    (0, 1),
]

LEGITIMACY_WEIGHTS = {
    "known_brand": 2.0,
    "domain_age": 1.0,
    "reviews": 1.0,
    "return_policy": 0.5,
}


def _score_price(price: float, max_budget: float = None) -> tuple[int, str]:
    """Score price from 1-5. Returns (score, evidence)."""
    if price <= 0:
        return 3, "Price unknown, assuming average"

    for threshold, score in PRICE_BRACKETS:
        if price < threshold:
            return score, f"${price:.0f} → price score {score}/5"

    return 1, f"${price:.0f} → price score 1/5 (expensive)"


def _score_quality(
    natural_fiber_pct: Optional[float], composition: Optional[dict] = None
) -> tuple[int, str]:
    """Score quality based on natural fiber content. Returns (score, evidence)."""
    if natural_fiber_pct is None:
        return 3, "Composition unknown, assuming average quality"

    pct = natural_fiber_pct
    for threshold, score in QUALITY_BRACKETS:
        if pct >= threshold:
            comp_str = ""
            if composition:
                top_fibers = sorted(
                    composition.items(), key=lambda x: x[1], reverse=True
                )[:3]
                comp_str = ", ".join(f"{k} {v:.0f}%" for k, v in top_fibers)
                comp_str = f" ({comp_str})"
            return (
                score,
                f"{pct:.0f}% natural fiber{comp_str} → quality score {score}/5",
            )

    return 1, f"{pct:.0f}% natural fiber → quality score 1/5"


def _score_legitimacy(
    known_brand: Optional[bool],
    domain_age_years: Optional[float],
    third_party_reviews: Optional[int],
    return_policy: Optional[bool],
) -> tuple[int, list[str]]:
    """
    Score legitimacy from 1-5 based on merchant signals.
    Returns (score, evidence_list).

    This is the GATE - below threshold means ineligible.
    """
    evidence = []
    points = 0
    max_points = 0

    max_points += 2
    if known_brand is True:
        points += 2
        evidence.append("✓ Recognized brand/retailer")
    elif known_brand is False:
        evidence.append("⚠ Unknown seller")
    else:
        points += 0.5
        evidence.append("? Brand recognition unknown")

    max_points += 1
    if domain_age_years is not None:
        if domain_age_years >= 5:
            points += 1
            evidence.append(f"✓ Established domain ({domain_age_years:.0f}+ years)")
        elif domain_age_years >= 2:
            points += 0.5
            evidence.append(f"~ Domain age {domain_age_years:.1f} years")
        else:
            evidence.append(f"⚠ New domain ({domain_age_years:.1f} years)")
    else:
        points += 0.3
        evidence.append("? Domain age unknown")

    max_points += 1
    if third_party_reviews is not None:
        if third_party_reviews >= 1000:
            points += 1
            evidence.append(
                f"✓ Well-reviewed ({third_party_reviews:,}+ external reviews)"
            )
        elif third_party_reviews >= 100:
            points += 0.5
            evidence.append(f"~ Some reviews ({third_party_reviews} external)")
        else:
            evidence.append(f"⚠ Few external reviews ({third_party_reviews})")
    else:
        points += 0.2
        evidence.append("? No external review data")

    max_points += 0.5
    if return_policy is True:
        points += 0.5
        evidence.append("✓ Has return policy")
    elif return_policy is False:
        evidence.append("⚠ No return policy found")

    raw_score = 1 + (points / max_points) * 4
    score = max(1, min(5, round(raw_score)))

    return score, evidence


def _compute_overall(price: int, quality: int, legitimacy: int) -> float:
    """
    Compute overall score using weighted geometric mean.

    Geometric mean penalizes weak axes harder than arithmetic mean.
    A product that's cheap but from a scammy seller won't rank well.
    """
    weights = {"price": 1.0, "quality": 1.2, "legitimacy": 1.5}
    total_weight = sum(weights.values())

    product = (
        (price ** weights["price"])
        * (quality ** weights["quality"])
        * (legitimacy ** weights["legitimacy"])
    )
    overall = product ** (1 / total_weight)

    return round(overall, 2)


def _determine_risk(
    legitimacy: int, overall: float
) -> Literal["low", "medium", "high"]:
    """Determine risk level based on scores."""
    if legitimacy >= 4 and overall >= 3.5:
        return "low"
    elif legitimacy >= 3 and overall >= 2.5:
        return "medium"
    else:
        return "high"


@tool
def score_product(
    url: str,
    price: float = None,
    natural_fiber_pct: float = None,
    composition: dict = None,
    known_brand: bool = None,
    domain_age_years: float = None,
    third_party_reviews: int = None,
    return_policy: bool = None,
) -> dict:
    """Score a product from 1-5 on price, quality and legitimacy using deterministic rules.

    The legitimacy score acts as a GATE: if below threshold, the product is ineligible
    regardless of how good the price or quality is. A cheap scam is still a scam.

    Args:
        url: The product page URL.
        price: Product price in USD.
        natural_fiber_pct: Percentage of natural fibers (0-100).
        composition: Fiber composition dict, e.g. {"cotton": 80, "polyester": 20}.
        known_brand: Whether the merchant is a recognized brand.
        domain_age_years: How old the seller's domain is.
        third_party_reviews: Number of external reviews of the seller.
        return_policy: Whether the seller has a return policy.

    Returns:
        Scores including:
        - price, quality, legitimacy: Individual scores 1-5
        - overall: Weighted geometric mean
        - eligible: False if legitimacy is below gate threshold
        - risk: "low", "medium", or "high"
        - evidence: List of scoring explanations
    """
    evidence = []

    price_score, price_evidence = _score_price(price or 0)
    evidence.append(price_evidence)

    quality_score, quality_evidence = _score_quality(natural_fiber_pct, composition)
    evidence.append(quality_evidence)

    legitimacy_score, legitimacy_evidence = _score_legitimacy(
        known_brand, domain_age_years, third_party_reviews, return_policy
    )
    evidence.extend(legitimacy_evidence)

    overall = _compute_overall(price_score, quality_score, legitimacy_score)

    eligible = legitimacy_score >= LEGITIMACY_GATE_THRESHOLD
    if not eligible:
        evidence.append(
            f" INELIGIBLE: Legitimacy {legitimacy_score}/5 below threshold {LEGITIMACY_GATE_THRESHOLD}"
        )

    risk = _determine_risk(legitimacy_score, overall)

    return Scores(
        url=url,
        price=price_score,
        quality=quality_score,
        legitimacy=legitimacy_score,
        overall=overall,
        eligible=eligible,
        risk=risk,
        evidence=evidence,
        available=True,
    ).model_dump()
