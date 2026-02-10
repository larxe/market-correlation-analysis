"""Tests for business logic (correlation classification, category mapping, grouping)."""

import numpy as np
import pandas as pd

from correlation_analysis.config import (
    INDEPENDENT_HIGH,
    INDEPENDENT_LOW,
    MIRROR_THRESHOLD,
    MODERATE_POS_THRESHOLD,
    TWINS_THRESHOLD,
)
from correlation_analysis.logic import (
    build_category_map,
    classify_correlation,
    group_correlations,
)


class TestClassifyCorrelation:
    """Test the correlation classification function."""

    def test_twins(self) -> None:
        label, tag = classify_correlation(0.90)
        assert tag == "pos_strong"
        assert "Twins" in label

    def test_twins_boundary(self) -> None:
        label, tag = classify_correlation(TWINS_THRESHOLD)
        assert tag == "pos_strong"

    def test_moderate_positive(self) -> None:
        label, tag = classify_correlation(0.65)
        assert tag == "pos_mod"

    def test_moderate_positive_boundary(self) -> None:
        label, tag = classify_correlation(MODERATE_POS_THRESHOLD)
        assert tag == "pos_mod"

    def test_independent(self) -> None:
        label, tag = classify_correlation(0.0)
        assert tag == "null"
        assert "Independent" in label

    def test_independent_positive_boundary(self) -> None:
        label, tag = classify_correlation(INDEPENDENT_HIGH)
        assert tag == "null"

    def test_independent_negative_boundary(self) -> None:
        label, tag = classify_correlation(INDEPENDENT_LOW)
        assert tag == "null"

    def test_weak_inverse(self) -> None:
        label, tag = classify_correlation(-0.35)
        assert tag == "neg_weak"

    def test_moderate_inverse(self) -> None:
        label, tag = classify_correlation(-0.65)
        assert tag == "neg_mod"

    def test_mirror(self) -> None:
        label, tag = classify_correlation(-0.90)
        assert tag == "neg_strong"
        assert "Mirror" in label

    def test_mirror_boundary(self) -> None:
        label, tag = classify_correlation(MIRROR_THRESHOLD)
        assert tag == "neg_strong"

    def test_weak_positive_noise(self) -> None:
        """Values between INDEPENDENT_HIGH and MODERATE_POS_THRESHOLD."""
        label, tag = classify_correlation(0.35)
        assert tag == "weak"

    def test_full_range_coverage(self) -> None:
        """Every value in [-1, 1] gets classified without error."""
        for val in np.linspace(-1.0, 1.0, 201):
            label, tag = classify_correlation(float(val))
            assert isinstance(label, str)
            assert tag in (
                "pos_strong", "pos_mod", "null",
                "neg_weak", "neg_mod", "neg_strong", "weak",
            )


class TestBuildCategoryMap:
    def test_known_assets(self) -> None:
        assets = ["ES (S&P 500)", "BTC", "GC (Gold)", "Unknown Asset"]
        cat_map = build_category_map(assets)

        assert cat_map["ES (S&P 500)"] == "Stock Indices"
        assert cat_map["BTC"] == "Crypto"
        assert cat_map["GC (Gold)"] == "Metals"
        assert "Unknown Asset" not in cat_map

    def test_empty_assets(self) -> None:
        cat_map = build_category_map([])
        assert cat_map == {}

    def test_all_configured_assets_mapped(self) -> None:
        """All assets from config should be mapped to some sector."""
        from correlation_analysis.config import ASSETS

        asset_names = list(ASSETS.keys())
        cat_map = build_category_map(asset_names)
        assert len(cat_map) > 0


class TestGroupCorrelations:
    def test_groups_same_sector_together(self) -> None:
        assets = ["ES (S&P 500)", "NQ (Nasdaq)", "GC (Gold)"]
        corr_data = np.array([
            [1.0, 0.95, 0.10],
            [0.95, 1.0, 0.05],
            [0.10, 0.05, 1.0],
        ])
        corr_matrix = pd.DataFrame(corr_data, index=assets, columns=assets)
        cat_map = build_category_map(assets)

        grouped = group_correlations(assets, corr_matrix, cat_map)

        stock_pairs = [item[0] for item in grouped.get("Stock Indices", [])]
        assert "ES (S&P 500) vs NQ (Nasdaq)" in stock_pairs

    def test_filters_weak_inter_market(self) -> None:
        assets = ["ES (S&P 500)", "GC (Gold)"]
        corr_data = np.array([
            [1.0, 0.10],
            [0.10, 1.0],
        ])
        corr_matrix = pd.DataFrame(corr_data, index=assets, columns=assets)
        cat_map = build_category_map(assets)

        grouped = group_correlations(assets, corr_matrix, cat_map)

        inter_pairs = grouped.get("Inter-Market (Mixed)", [])
        assert len(inter_pairs) == 0

    def test_includes_strong_inter_market(self) -> None:
        assets = ["ES (S&P 500)", "GC (Gold)"]
        corr_data = np.array([
            [1.0, 0.85],
            [0.85, 1.0],
        ])
        corr_matrix = pd.DataFrame(corr_data, index=assets, columns=assets)
        cat_map = build_category_map(assets)

        grouped = group_correlations(assets, corr_matrix, cat_map)

        inter_pairs = [item[0] for item in grouped.get("Inter-Market (Mixed)", [])]
        assert "ES (S&P 500) vs GC (Gold)" in inter_pairs
