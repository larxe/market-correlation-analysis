"""Tests for data module (using synthetic data, no network calls)."""

import numpy as np
import pandas as pd
import pytest

from correlation_analysis.config import MEDIUM_TERM_DAYS, SHORT_TERM_DAYS
from correlation_analysis.data import compute_correlation_matrices


def _make_synthetic_prices(
    n_assets: int = 5, n_days: int = 200, seed: int = 42
) -> pd.DataFrame:
    """Generate synthetic price data for testing."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end="2025-01-15", periods=n_days)
    names = [f"Asset_{i}" for i in range(n_assets)]

    # Random walk prices
    returns = rng.normal(0.0005, 0.02, size=(n_days, n_assets))
    prices = 100 * np.exp(np.cumsum(returns, axis=0))
    return pd.DataFrame(prices, index=dates, columns=names)


class TestComputeCorrelationMatrices:
    def test_returns_two_dataframes(self) -> None:
        data = _make_synthetic_prices()
        corr_short, corr_medium = compute_correlation_matrices(data)
        assert isinstance(corr_short, pd.DataFrame)
        assert isinstance(corr_medium, pd.DataFrame)

    def test_matrices_are_square(self) -> None:
        data = _make_synthetic_prices(n_assets=4)
        corr_short, corr_medium = compute_correlation_matrices(data)
        assert corr_short.shape[0] == corr_short.shape[1]
        assert corr_medium.shape[0] == corr_medium.shape[1]

    def test_diagonal_is_one(self) -> None:
        data = _make_synthetic_prices()
        corr_short, corr_medium = compute_correlation_matrices(data)
        np.testing.assert_allclose(np.diag(corr_short.values), 1.0, atol=1e-10)
        np.testing.assert_allclose(np.diag(corr_medium.values), 1.0, atol=1e-10)

    def test_matrices_are_symmetric(self) -> None:
        data = _make_synthetic_prices()
        corr_short, corr_medium = compute_correlation_matrices(data)
        np.testing.assert_allclose(
            corr_short.values, corr_short.values.T, atol=1e-10
        )
        np.testing.assert_allclose(
            corr_medium.values, corr_medium.values.T, atol=1e-10
        )

    def test_values_in_valid_range(self) -> None:
        data = _make_synthetic_prices()
        corr_short, corr_medium = compute_correlation_matrices(data)
        assert (corr_short.values >= -1.0 - 1e-10).all()
        assert (corr_short.values <= 1.0 + 1e-10).all()
        assert (corr_medium.values >= -1.0 - 1e-10).all()
        assert (corr_medium.values <= 1.0 + 1e-10).all()

    def test_column_names_preserved(self) -> None:
        data = _make_synthetic_prices(n_assets=3)
        corr_short, corr_medium = compute_correlation_matrices(data)
        assert list(corr_short.columns) == list(data.columns)
        assert list(corr_medium.columns) == list(data.columns)

    def test_perfectly_correlated_assets(self) -> None:
        """Two identical assets should have correlation = 1."""
        dates = pd.bdate_range(end="2025-01-15", periods=200)
        prices = np.linspace(100, 150, 200)
        data = pd.DataFrame(
            {"A": prices, "B": prices, "C": prices[::-1]},
            index=dates,
        )
        corr_short, _ = compute_correlation_matrices(data)
        assert corr_short.loc["A", "B"] == pytest.approx(1.0, abs=1e-10)

    def test_insufficient_data_still_computes(self) -> None:
        """With very few rows, the correlation might have NaNs but should not crash."""
        dates = pd.bdate_range(end="2025-01-15", periods=MEDIUM_TERM_DAYS + 5)
        rng = np.random.default_rng(0)
        data = pd.DataFrame(
            rng.normal(size=(MEDIUM_TERM_DAYS + 5, 3)),
            index=dates,
            columns=["X", "Y", "Z"],
        )
        corr_short, corr_medium = compute_correlation_matrices(data)
        assert corr_short.shape == (3, 3)
        assert corr_medium.shape == (3, 3)


class TestSyntheticDataHelper:
    def test_generates_correct_shape(self) -> None:
        data = _make_synthetic_prices(n_assets=7, n_days=100)
        assert data.shape == (100, 7)

    def test_all_positive_prices(self) -> None:
        data = _make_synthetic_prices()
        assert (data.values > 0).all()

    def test_reproducible_with_seed(self) -> None:
        d1 = _make_synthetic_prices(seed=123)
        d2 = _make_synthetic_prices(seed=123)
        pd.testing.assert_frame_equal(d1, d2)
