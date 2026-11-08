from quickshop.evidence.tool import fetch_product_evidence
from quickshop.tools.search import search_listings
from quickshop.tools.merchant import check_merchant
from quickshop.tools.scoring import score_product
from quickshop.tools.user import ask_user

# 5 Tools
DEFAULT_TOOLS = [
    search_listings,
    check_merchant,
    fetch_product_evidence,
    score_product,
    ask_user,
]
