"""Configuration constants for the Market Correlation Analysis tool."""

from __future__ import annotations

# --- Data Download ---
DOWNLOAD_PERIOD: str = "6mo"
DOWNLOAD_INTERVAL: str = "1d"

# --- Correlation Windows ---
SHORT_TERM_DAYS: int = 15
MEDIUM_TERM_DAYS: int = 60

# --- Correlation Thresholds ---
TWINS_THRESHOLD: float = 0.80
MODERATE_POS_THRESHOLD: float = 0.50
INDEPENDENT_LOW: float = -0.20
INDEPENDENT_HIGH: float = 0.20
WEAK_NEG_THRESHOLD: float = -0.50
MIRROR_THRESHOLD: float = -0.80

# --- Display Thresholds ---
WEAK_CORRELATION_DISPLAY: float = 0.30
DIFF_POSITIVE_THRESHOLD: float = 0.10
DIFF_NEGATIVE_THRESHOLD: float = -0.10
PCT_CHANGE_MIN_DENOMINATOR: float = 0.01
NEW_CORRELATION_THRESHOLD: float = 0.10

# --- GUI ---
WINDOW_FALLBACK_GEOMETRY: str = "1400x900"
FIGURE_SIZE: tuple[int, int] = (14, 10)
FIGURE_DPI: int = 100
EXPORT_DPI: int = 300

# --- Colors ---
COLOR_POSITIVE: str = "#006400"
COLOR_NEGATIVE: str = "#8B0000"
COLOR_NEUTRAL: str = "black"
COLOR_HIGHLIGHT: str = "#0000FF"

# --- Asset Configuration ---
ASSETS: dict[str, str] = {
    # Currencies & Fixed Income
    "6B (Pound)": "6B=F",
    "ZN (10Y Bond)": "ZN=F",
    "6J (Yen)": "6J=F",
    "6E (Euro)": "6E=F",
    "6S (Swiss Franc)": "6S=F",
    "6N (NZD)": "6N=F",
    "6A (AUD)": "6A=F",
    "6C (CAD)": "6C=F",
    "ZT (2Y Bond)": "ZT=F",
    # Grains & Meats
    "ZW (Wheat)": "ZW=F",
    "ZS (Soybean)": "ZS=F",
    "ZC (Corn)": "ZC=F",
    "ZM (Soy Meal)": "ZM=F",
    "ZL (Soy Oil)": "ZL=F",
    "LE (Live Cattle)": "LE=F",
    "HE (Lean Hogs)": "HE=F",
    # Crypto & Metals
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "GC (Gold)": "GC=F",
    "SI (Silver)": "SI=F",
    "HG (Copper)": "HG=F",
    "PL (Platinum)": "PL=F",
    # Energies
    "CL (WTI Crude)": "CL=F",
    "RB (Gasoline)": "RB=F",
    "NG (Nat Gas)": "NG=F",
    "HO (Heating Oil)": "HO=F",
    # Stock Indices
    "ES (S&P 500)": "ES=F",
    "NQ (Nasdaq)": "NQ=F",
    "YM (Dow Jones)": "YM=F",
    "RTY (Russell)": "RTY=F",
}

# --- Sector Definitions (for grouping in Strong Correlations tab) ---
SECTORS: dict[str, list[str]] = {
    "Stock Indices": ["ES", "NQ", "YM", "RTY"],
    "Energies": ["CL", "RB", "NG", "HO"],
    "Metals": ["GC", "SI", "HG", "PL"],
    "Crypto": ["BTC", "ETH"],
    "Currencies": ["6B", "6J", "6E", "6S", "6N", "6A", "6C"],
    "Bonds/Fixed Income": ["ZN", "ZT"],
    "Agriculture (Grains)": ["ZW", "ZS", "ZC", "ZM", "ZL"],
    "Livestock (Meats)": ["LE", "HE"],
}
