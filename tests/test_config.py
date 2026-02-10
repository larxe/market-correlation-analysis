"""Tests for configuration module."""

from correlation_analysis.config import (
    ASSETS,
    DOWNLOAD_INTERVAL,
    DOWNLOAD_PERIOD,
    INDEPENDENT_HIGH,
    INDEPENDENT_LOW,
    MEDIUM_TERM_DAYS,
    MIRROR_THRESHOLD,
    MODERATE_POS_THRESHOLD,
    SECTORS,
    SHORT_TERM_DAYS,
    TWINS_THRESHOLD,
    WEAK_NEG_THRESHOLD,
)


class TestAssetConfig:
    def test_assets_not_empty(self) -> None:
        assert len(ASSETS) > 0

    def test_assets_have_ticker_values(self) -> None:
        for name, ticker in ASSETS.items():
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(ticker, str) and len(ticker) > 0

    def test_no_duplicate_tickers(self) -> None:
        tickers = list(ASSETS.values())
        assert len(tickers) == len(set(tickers)), "Duplicate tickers found"

    def test_no_duplicate_names(self) -> None:
        names = list(ASSETS.keys())
        assert len(names) == len(set(names)), "Duplicate asset names found"


class TestSectorConfig:
    def test_sectors_not_empty(self) -> None:
        assert len(SECTORS) > 0

    def test_all_sectors_have_tickers(self) -> None:
        for sector, tickers in SECTORS.items():
            assert len(tickers) > 0, f"Sector '{sector}' has no tickers"

    def test_sector_tickers_match_assets(self) -> None:
        """Every sector ticker prefix should match at least one asset."""
        asset_names = list(ASSETS.keys())
        for sector, tickers in SECTORS.items():
            for ticker_prefix in tickers:
                matches = [
                    a
                    for a in asset_names
                    if a.startswith(ticker_prefix + " ") or a == ticker_prefix
                ]
                assert len(matches) > 0, (
                    f"Ticker prefix '{ticker_prefix}' in sector '{sector}' "
                    f"does not match any asset"
                )

    def test_no_overlapping_tickers_across_sectors(self) -> None:
        """A ticker prefix should only appear in one sector."""
        all_tickers: list[str] = []
        for tickers in SECTORS.values():
            all_tickers.extend(tickers)
        assert len(all_tickers) == len(set(all_tickers)), (
            "Ticker prefix appears in multiple sectors"
        )


class TestThresholds:
    def test_correlation_windows_positive(self) -> None:
        assert SHORT_TERM_DAYS > 0
        assert MEDIUM_TERM_DAYS > 0

    def test_short_term_less_than_medium(self) -> None:
        assert SHORT_TERM_DAYS < MEDIUM_TERM_DAYS

    def test_threshold_ordering(self) -> None:
        """Thresholds should form a consistent ordering on the correlation scale."""
        assert MIRROR_THRESHOLD < WEAK_NEG_THRESHOLD
        assert WEAK_NEG_THRESHOLD < INDEPENDENT_LOW
        assert INDEPENDENT_LOW < INDEPENDENT_HIGH
        assert INDEPENDENT_HIGH < MODERATE_POS_THRESHOLD
        assert MODERATE_POS_THRESHOLD < TWINS_THRESHOLD

    def test_thresholds_in_valid_range(self) -> None:
        """Correlation thresholds must be between -1 and 1."""
        for val in [
            TWINS_THRESHOLD,
            MODERATE_POS_THRESHOLD,
            INDEPENDENT_HIGH,
            INDEPENDENT_LOW,
            WEAK_NEG_THRESHOLD,
            MIRROR_THRESHOLD,
        ]:
            assert -1.0 <= val <= 1.0, f"Threshold {val} is out of [-1, 1] range"

    def test_download_period_format(self) -> None:
        assert DOWNLOAD_PERIOD in ("1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max")

    def test_download_interval_format(self) -> None:
        assert DOWNLOAD_INTERVAL in ("1d", "1wk", "1mo")
