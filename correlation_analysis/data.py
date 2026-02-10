"""Data downloading and correlation matrix computation."""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
import yfinance as yf

from correlation_analysis.config import (
    ASSETS,
    DOWNLOAD_INTERVAL,
    DOWNLOAD_PERIOD,
    MEDIUM_TERM_DAYS,
    SHORT_TERM_DAYS,
)

logger = logging.getLogger(__name__)


def download_market_data() -> Optional[pd.DataFrame]:
    """Download closing prices for all configured assets from Yahoo Finance.

    Returns:
        DataFrame with columns renamed to human-readable asset names,
        or None if download fails.
    """
    tickers = list(ASSETS.values())
    logger.info("Downloading data for %d markets...", len(tickers))

    try:
        downloaded = yf.download(
            tickers,
            period=DOWNLOAD_PERIOD,
            interval=DOWNLOAD_INTERVAL,
            progress=False,
        )
    except Exception:
        logger.exception("Failed to download market data")
        return None

    if downloaded.empty:
        logger.error("Downloaded data is empty")
        return None

    if "Close" in downloaded.columns:
        data = downloaded["Close"]
    elif "Adj Close" in downloaded.columns:
        data = downloaded["Adj Close"]
    else:
        logger.warning("No 'Close' or 'Adj Close' columns found; using first level")
        data = downloaded.iloc[:, : len(tickers)]

    inv_map = {v: k for k, v in ASSETS.items()}
    data = data.rename(columns=inv_map)
    return data


def compute_correlation_matrices(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute short-term and medium-term correlation matrices.

    Args:
        data: DataFrame of closing prices with asset-name columns.

    Returns:
        Tuple of (short_term_correlation, medium_term_correlation) DataFrames.
    """
    corr_short = data.pct_change(SHORT_TERM_DAYS).dropna().corr()
    corr_medium = data.pct_change(MEDIUM_TERM_DAYS).dropna().corr()
    logger.info(
        "Computed correlation matrices: %d-day and %d-day",
        SHORT_TERM_DAYS,
        MEDIUM_TERM_DAYS,
    )
    return corr_short, corr_medium


def fetch_correlations() -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Download data and return both correlation matrices.

    Returns:
        Tuple of (short_term, medium_term) correlation DataFrames,
        or (None, None) on failure.
    """
    data = download_market_data()
    if data is None:
        return None, None
    return compute_correlation_matrices(data)
