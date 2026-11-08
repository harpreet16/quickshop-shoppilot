BENCHMARK_QUERIES = [
    {
        "id": "q1",
        "query": "black jeans under $60",
        "category": "basic",
        "expected_behavior": "Should return affordable black jeans from trusted sellers",
    },
    {
        "id": "q2",
        "query": "white cotton t-shirt under $30",
        "category": "basic",
        "expected_behavior": "Should prioritize high natural fiber content",
    },
    {
        "id": "q3",
        "query": "wool sweater under $100",
        "category": "basic",
        "expected_behavior": "Should find wool (natural fiber) sweaters",
    },
    {
        "id": "q4",
        "query": "100% cotton dress shirt for work",
        "category": "quality",
        "expected_behavior": "Should prioritize pure cotton over blends",
    },
    {
        "id": "q5",
        "query": "linen pants for summer",
        "category": "quality",
        "expected_behavior": "Should find linen (natural fiber) pants",
    },
    {
        "id": "q6",
        "query": "cheap designer jeans under $40",
        "category": "trust",
        "expected_behavior": "Should flag suspiciously cheap designer items or unknown sellers",
    },
    {
        "id": "q7",
        "query": "silk blouse from a reputable brand",
        "category": "trust",
        "expected_behavior": "Should prioritize known brands over unknowns",
    },
    {
        "id": "q8",
        "query": "warm winter jacket under $150",
        "category": "edge",
        "expected_behavior": "May need to handle synthetic insulation (not natural fiber)",
    },
    {
        "id": "q9",
        "query": "formal suit under $200",
        "category": "edge",
        "expected_behavior": "Multi-piece item, higher budget",
    },
    {
        "id": "q10",
        "query": "athletic shorts for running",
        "category": "edge",
        "expected_behavior": "Synthetic materials may be appropriate for performance",
    },
    {
        "id": "q11",
        "query": "gucci bag under $50",
        "category": "abstain",
        "expected_behavior": "Should abstain - likely counterfeit at this price",
    },
    {
        "id": "q12",
        "query": "cashmere sweater under $20",
        "category": "abstain",
        "expected_behavior": "Should abstain or warn - real cashmere not available at this price",
    },
]


def get_queries_by_category(category: str = None) -> list:
    """Get benchmark queries, optionally filtered by category."""
    if category is None:
        return BENCHMARK_QUERIES
    return [q for q in BENCHMARK_QUERIES if q["category"] == category]


def get_query_by_id(query_id: str) -> dict:
    """Get a specific benchmark query by ID."""
    for q in BENCHMARK_QUERIES:
        if q["id"] == query_id:
            return q
    return None
