# Dataset 2 — 25 real shopping requests collected from Reddit (r/malefashionadvice and
# r/femalefashionadvice). PII (names, body measurements, specific usernames) has been removed.
# Each entry records the source subreddit so the origin of the request is traceable.
#
# Format matches eval/benchmark.py exactly so the same runner and metrics code works on both.

DATASET2_QUERIES = [
    # ------------------------------------------------------------------ basic
    {
        "id": "d2q1",
        "query": "straight leg chino pants with more room in the thighs, size 32 waist, under $80",
        "category": "basic",
        "expected_behavior": "Should find well-fitting chinos from trusted brands within budget",
        "source": "r/malefashionadvice — 'Go-To Chino Recommendations'",
    },
    {
        "id": "d2q2",
        "query": "men's t-shirts that don't shrink or go wavy at the collar after washing, under $40",
        "category": "basic",
        "expected_behavior": "Should prioritise 100% cotton or long-staple cotton options from trusted sellers",
        "source": "r/malefashionadvice — 'Best t shirts for men? Quality brands that last'",
    },
    {
        "id": "d2q3",
        "query": "white oxford cloth button-down shirt, slightly wider in the shoulders, under $120",
        "category": "basic",
        "expected_behavior": "Should find cotton shirts from established brands that fit broader shoulders",
        "source": "r/malefashionadvice — 'OCBDs in the $70–$130 that fits slightly broad shoulders'",
    },
    {
        "id": "d2q4",
        "query": "women's knee-high boots, comfortable for all-day wear, under $200",
        "category": "basic",
        "expected_behavior": "Should find boots from reputable brands with strong reviews",
        "source": "r/femalefashionadvice — 'Recommendations on what style and where to get knee high leather boots'",
    },
    {
        "id": "d2q5",
        "query": "women's cotton or linen tops for a long torso under $70",
        "category": "basic",
        "expected_behavior": "Should find natural-fiber tops long enough to stay tucked for a longer torso",
        "source": "r/femalefashionadvice — 'Places to buy shirts for long torso?'",
    },
    # ------------------------------------------------------------------ quality
    {
        "id": "d2q6",
        "query": "loose-fitting men's shirt in linen or 100% cotton, under $200",
        "category": "quality",
        "expected_behavior": "Should prioritise 100% natural-fiber shirts and penalise synthetic blends",
        "source": "r/malefashionadvice — 'Loose-fitting, natural fabric, ~$200 USD-range shirt recommendations'",
    },
    {
        "id": "d2q7",
        "query": "100% cashmere scarf under $150",
        "category": "quality",
        "expected_behavior": "Should find genuine cashmere and flag likely blends or suspect sellers",
        "source": "r/malefashionadvice — 'Cashmere scarf'",
    },
    {
        "id": "d2q8",
        "query": "merino wool or cashmere crewneck sweater for a smart-casual wardrobe under $200",
        "category": "quality",
        "expected_behavior": "Should prioritise high natural wool/cashmere content and established brands",
        "source": "r/malefashionadvice — 'Is it actually cheaper to dress well in Italy compared to France? (Sartorial / quality fabrics)'",
    },
    {
        "id": "d2q9",
        "query": "wool scarf to wear with a navy peacoat, natural fiber only, under $80",
        "category": "quality",
        "expected_behavior": "Should find 100% wool scarves and discard synthetic alternatives",
        "source": "r/malefashionadvice — 'Looking for scarf suggestions'",
    },
    {
        "id": "d2q10",
        "query": "women's soft, long-lasting blouse or top in natural fabric under $80",
        "category": "quality",
        "expected_behavior": "Should score composition heavily; penalise viscose-heavy or polyester blends",
        "source": "r/femalefashionadvice — 'Long lasting, ultra soft fabrics'",
    },
    {
        "id": "d2q11",
        "query": "women's wool-blend coat that actually keeps you warm in winter, under $300",
        "category": "quality",
        "expected_behavior": "Should prioritise high wool percentage and flag mostly-polyester coats",
        "source": "r/femalefashionadvice — 'What\\'s Your Warmest Wool or Wool-Blend Coat?'",
    },
    {
        "id": "d2q12",
        "query": "silk blouse for the office from a reputable brand under $120",
        "category": "quality",
        "expected_behavior": "Should distinguish 100% silk from polyester 'satin' imposters and flag unknown sellers",
        "source": "r/femalefashionadvice — general office wear thread",
    },
    # ------------------------------------------------------------------ trust
    {
        "id": "d2q13",
        "query": "classic mac coat or short trench coat in natural fabric under $350",
        "category": "trust",
        "expected_behavior": "Should verify seller legitimacy carefully; classic trench territory has counterfeit risk",
        "source": "r/malefashionadvice — 'Looking for a mac coat — what are some good options?'",
    },
    {
        "id": "d2q14",
        "query": "slim-fit henley shirt in 100% cotton under $60 from a trusted brand",
        "category": "trust",
        "expected_behavior": "Should check seller credibility and reject cheap synthetic blends",
        "source": "r/malefashionadvice — 'Any recommendations for a good quality, slim-fitting Henley in Canada?'",
    },
    {
        "id": "d2q15",
        "query": "quality cotton button-down dress shirt, comparable to Buck Mason, under $100",
        "category": "trust",
        "expected_behavior": "Should find legitimate brands at this price point and explain quality differences",
        "source": "r/malefashionadvice — 'Is it worth spending more?' (Abercrombie vs Buck Mason)",
    },
    {
        "id": "d2q16",
        "query": "functional waterproof women's ankle boots from a legitimate brand under $150",
        "category": "trust",
        "expected_behavior": "Should prioritise established footwear brands and flag unknown dropship shops",
        "source": "r/femalefashionadvice — 'Boots that are aesthetic AND functional'",
    },
    {
        "id": "d2q17",
        "query": "affordable ethical women's winter jacket from a reputable brand under $200",
        "category": "trust",
        "expected_behavior": "Should verify brand legitimacy; 'ethical' claims require extra seller scrutiny",
        "source": "r/femalefashionadvice — 'Affordable European fashion brands'",
    },
    # ------------------------------------------------------------------ edge
    {
        "id": "d2q18",
        "query": "jeans for men with big thighs and a narrow waist, size 32 waist, under $100",
        "category": "edge",
        "expected_behavior": "Should handle unusual fit requirements and may note limited options",
        "source": "r/malefashionadvice — 'How to find the right trousers as a man with a big butt?'",
    },
    {
        "id": "d2q19",
        "query": "warm waterproof winter jacket for temperatures around -15 Celsius under $200",
        "category": "edge",
        "expected_behavior": "May note that synthetic insulation is more practical; should not penalise heavily for synthetic fill",
        "source": "r/malefashionadvice — 'Winter jacket' (Polish winter context)",
    },
    {
        "id": "d2q20",
        "query": "women's business formal dress trousers that fit comfortably, natural fabric preferred, under $120",
        "category": "edge",
        "expected_behavior": "Should attempt natural fibers in a formal trouser; may flag limited options",
        "source": "r/femalefashionadvice — 'Been awhile since I\\'ve shopped for business formal'",
    },
    {
        "id": "d2q21",
        "query": "women's fleece-lined thermal tights that don't pill, under $40",
        "category": "edge",
        "expected_behavior": "Fleece tights are inherently synthetic; agent should not over-penalise quality score for this category",
        "source": "r/femalefashionadvice — 'fleece tights that don\\'t pill'",
    },
    {
        "id": "d2q22",
        "query": "men's suit for a larger build, plus-size friendly, under $400",
        "category": "edge",
        "expected_behavior": "Should handle plus-size suit request and prioritise retailers with extended sizing",
        "source": "r/malefashionadvice — 'Wedding suits for a fat guy?'",
    },
    # ------------------------------------------------------------------ abstain
    {
        "id": "d2q23",
        "query": "100% cashmere luxury sweater under $50",
        "category": "abstain",
        "expected_behavior": "Should abstain or warn strongly — genuine cashmere at this price is implausible",
        "source": "r/femalefashionadvice — cashmere pricing discussion threads",
    },
    {
        "id": "d2q24",
        "query": "fully canvassed wool suit jacket under $100",
        "category": "abstain",
        "expected_behavior": "Should abstain — fully canvassed wool construction is not available at this price",
        "source": "r/malefashionadvice — sartorial quality fabric discussions",
    },
    {
        "id": "d2q25",
        "query": "real 100% silk blouse under $20",
        "category": "abstain",
        "expected_behavior": "Should abstain — 100% silk at this price is almost certainly mislabelled or counterfeit",
        "source": "r/femalefashionadvice — silk vs polyester satin discussions",
    },
]


def get_queries_by_category(category: str = None) -> list:
    """Get dataset-2 queries, optionally filtered by category."""
    if category is None:
        return DATASET2_QUERIES
    return [q for q in DATASET2_QUERIES if q["category"] == category]


def get_query_by_id(query_id: str) -> dict:
    """Get a specific dataset-2 query by ID."""
    for q in DATASET2_QUERIES:
        if q["id"] == query_id:
            return q
    return None
