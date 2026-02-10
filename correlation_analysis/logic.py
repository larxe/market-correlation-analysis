"""Pure business logic for correlation classification and grouping (no GUI deps)."""

from __future__ import annotations

import pandas as pd

from correlation_analysis.config import (
    INDEPENDENT_HIGH,
    INDEPENDENT_LOW,
    MIRROR_THRESHOLD,
    MODERATE_POS_THRESHOLD,
    SECTORS,
    TWINS_THRESHOLD,
    WEAK_NEG_THRESHOLD,
)


def classify_correlation(val: float) -> tuple[str, str]:
    """Return (interpretation_label, tag) for a correlation value.

    Tags: pos_strong, pos_mod, null, neg_weak, neg_mod, neg_strong, weak.
    """
    if val >= TWINS_THRESHOLD:
        return "Twins (High Risk)", "pos_strong"
    if val >= MODERATE_POS_THRESHOLD:
        return "Moderate Positive", "pos_mod"
    if INDEPENDENT_LOW <= val <= INDEPENDENT_HIGH:
        return "Independent (Diversify)", "null"
    if WEAK_NEG_THRESHOLD < val < INDEPENDENT_LOW:
        return "Weak Inverse", "neg_weak"
    if MIRROR_THRESHOLD < val <= WEAK_NEG_THRESHOLD:
        return "Moderate Inverse", "neg_mod"
    if val <= MIRROR_THRESHOLD:
        return "Mirror (Hedging)", "neg_strong"
    return "Weak Positive / Noise", "weak"


def build_category_map(assets: list[str]) -> dict[str, str]:
    """Map each asset name to its sector based on ticker prefix."""
    cat_map: dict[str, str] = {}
    for cat, tickers in SECTORS.items():
        for ticker_key in tickers:
            for asset_full in assets:
                if asset_full.startswith(ticker_key + " ") or asset_full == ticker_key:
                    cat_map[asset_full] = cat
    return cat_map


def group_correlations(
    assets: list[str],
    corr_matrix: pd.DataFrame,
    cat_map: dict[str, str],
) -> dict[str, list[tuple[str, float, float, str, str]]]:
    """Group and filter correlation pairs by sector.

    Returns dict mapping sector name to list of
    (pair_label, correlation, r_squared_pct, interpretation, tag).
    """
    grouped: dict[str, list[tuple[str, float, float, str, str]]] = {
        cat: [] for cat in SECTORS
    }
    grouped["Inter-Market (Mixed)"] = []

    for i in range(len(assets)):
        for j in range(i + 1, len(assets)):
            asset_a = assets[i]
            asset_b = assets[j]
            val = float(corr_matrix.iloc[i, j])
            r2 = (val**2) * 100

            cat_a = cat_map.get(asset_a, "Others")
            cat_b = cat_map.get(asset_b, "Others")

            tipo, tag = classify_correlation(val)

            if cat_a == cat_b and cat_a != "Others":
                grouped[cat_a].append(
                    (f"{asset_a} vs {asset_b}", val, r2, tipo, tag)
                )
            elif tag not in ("weak", "null"):
                grouped["Inter-Market (Mixed)"].append(
                    (f"{asset_a} vs {asset_b}", val, r2, tipo, tag)
                )

    return grouped
