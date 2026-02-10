"""Entry point for the Market Correlation Analysis application."""

from __future__ import annotations

import logging
import sys

from correlation_analysis.data import fetch_correlations
from correlation_analysis.gui import run_app

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Download market data, compute correlations, and launch the GUI."""
    logger.info("Starting Market Correlation Analysis...")
    corr_short, corr_medium = fetch_correlations()

    if corr_short is None or corr_medium is None:
        logger.error("Could not obtain data to generate correlation matrices.")
        sys.exit(1)

    run_app(corr_short, corr_medium)


if __name__ == "__main__":
    main()
