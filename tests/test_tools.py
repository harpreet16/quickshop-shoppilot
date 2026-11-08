# Tests for the tool implementations
import pytest

from quickshop.tools.search import search_listings
from quickshop.tools.merchant import check_merchant
from quickshop.tools.scoring import score_product


class TestSearchListings:
    """Tests for the SerpAPI search tool."""

    def test_search_returns_list(self, monkeypatch):
        """Search should return a list."""
        monkeypatch.setenv("SERPAPI_KEY", "")
        result = search_listings("black jeans")
        assert isinstance(result, list)

    def test_search_without_key_returns_error(self, monkeypatch):
        """Without API key, should return error dict."""
        monkeypatch.delenv("SERPAPI_KEY", raising=False)
        result = search_listings("test query")
        assert len(result) == 1
        assert "error" in result[0] or "available" in result[0]


class TestCheckMerchant:
    """Tests for the merchant trust checking tool."""

    def test_known_brand_is_recognized(self):
        """Known brands should be flagged as known."""
        result = check_merchant("Levi's")
        assert result["known_brand"] is True
        assert result["available"] is True

    def test_unknown_seller_not_recognized(self):
        """Unknown sellers should not be flagged as known brands."""
        result = check_merchant("RandomNoNameStore12345")
        assert result["known_brand"] is False

    def test_major_retailers_recognized(self):
        """Major retailers should all be recognized."""
        retailers = ["Nordstrom", "Target", "Amazon", "Zara", "H&M"]
        for retailer in retailers:
            result = check_merchant(retailer)
            assert result["known_brand"] is True, f"{retailer} should be recognized"

    def test_returns_merchant_signals_schema(self):
        """Should return all expected fields."""
        result = check_merchant("Nike")
        assert "merchant" in result
        assert "known_brand" in result
        assert "domain_age_years" in result
        assert "third_party_reviews" in result
        assert "return_policy" in result
        assert "available" in result


class TestScoreProduct:
    """Tests for the deterministic scoring tool."""

    def test_cheap_good_trusted_is_eligible(self):
        """A cheap, quality product from trusted seller should be eligible."""
        result = score_product(
            url="https://test.com/product",
            price=45,
            natural_fiber_pct=90,
            known_brand=True,
            domain_age_years=10,
            third_party_reviews=5000,
        )
        assert result["eligible"] is True
        assert result["risk"] == "low"
        assert result["price"] >= 4
        assert result["quality"] >= 4
        assert result["legitimacy"] >= 4

    def test_cheap_sketchy_is_ineligible(self):
        """A cheap product from sketchy seller should fail legitimacy gate."""
        result = score_product(
            url="https://sketchy.xyz/deal",
            price=15,
            natural_fiber_pct=80,
            known_brand=False,
            domain_age_years=0.3,
            third_party_reviews=5,
        )
        assert result["eligible"] is False
        assert result["legitimacy"] < 3
        assert result["risk"] == "high"

    def test_legitimacy_gate_blocks_bad_sellers(self):
        """The legitimacy gate should block products regardless of price/quality."""
        result = score_product(
            url="https://scam.site/amazing-deal",
            price=20,
            natural_fiber_pct=100,
            known_brand=False,
            domain_age_years=0.1,
            third_party_reviews=0,
            return_policy=False,
        )
        assert result["eligible"] is False

    def test_scores_are_1_to_5(self):
        """All scores should be integers from 1 to 5."""
        result = score_product(
            url="https://test.com/item",
            price=50,
            natural_fiber_pct=50,
            known_brand=True,
        )
        for score_key in ["price", "quality", "legitimacy"]:
            assert 1 <= result[score_key] <= 5
            assert isinstance(result[score_key], int)

    def test_overall_uses_geometric_mean(self):
        """Overall score should be weighted geometric mean, not arithmetic."""
        result = score_product(
            url="https://test.com/item",
            price=50,
            natural_fiber_pct=70,
            known_brand=True,
            domain_age_years=5,
            third_party_reviews=1000,
        )
        assert isinstance(result["overall"], float)
        assert 1 <= result["overall"] <= 5

    def test_evidence_list_is_populated(self):
        """Evidence list should explain the scoring."""
        result = score_product(
            url="https://test.com/item",
            price=45,
            natural_fiber_pct=85,
            known_brand=True,
        )
        assert len(result["evidence"]) > 0
        assert any("price" in e.lower() for e in result["evidence"])

    def test_returns_scores_schema(self):
        """Should return all expected fields."""
        result = score_product(url="https://test.com/item", price=50)
        assert "url" in result
        assert "price" in result
        assert "quality" in result
        assert "legitimacy" in result
        assert "overall" in result
        assert "eligible" in result
        assert "risk" in result
        assert "evidence" in result
        assert "available" in result


class TestScoringBrackets:
    """Tests for specific scoring bracket thresholds."""

    def test_price_brackets(self):
        """Test price scoring brackets."""
        assert score_product(url="test", price=25)["price"] == 5
        assert score_product(url="test", price=40)["price"] == 4
        assert score_product(url="test", price=65)["price"] == 3
        assert score_product(url="test", price=100)["price"] == 2
        assert score_product(url="test", price=150)["price"] == 1

    def test_quality_brackets(self):
        """Test quality scoring brackets."""
        assert score_product(url="test", natural_fiber_pct=95)["quality"] == 5
        assert score_product(url="test", natural_fiber_pct=80)["quality"] == 4
        assert score_product(url="test", natural_fiber_pct=60)["quality"] == 3
        assert score_product(url="test", natural_fiber_pct=40)["quality"] == 2
        assert score_product(url="test", natural_fiber_pct=20)["quality"] == 1
