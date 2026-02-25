"""Lucid Trading futures commissions reference.

Maps each futures contract to its Lucid Trading commission (per side, in USD).
Lucid Trading is a prop firm that supports ~36 CME-approved futures contracts.

Data sourced from Lucid Trading Help Center and third-party reviews (Feb 2025).
For the most up-to-date figures, see:
https://support.lucidtrading.com/en/articles/11508978-approved-products-and-commissions

All commissions are per side (multiply by 2 for round-trip).
Spreads are raw/market-driven on CME, CBOT, NYMEX, COMEX — no firm markup.
"""

from __future__ import annotations

# Commission per side in USD for each approved contract on Lucid Trading.
# None means the contract is NOT available on Lucid Trading.

LUCID_COMMISSIONS: dict[str, float | None] = {
    # ── Equity Index Futures (E-mini) ── Exchange: CME/CBOT
    "ES": 1.75,    # E-mini S&P 500
    "NQ": 1.75,    # E-mini Nasdaq-100
    "YM": 1.75,    # E-mini Dow Jones
    "RTY": 1.75,   # E-mini Russell 2000

    # ── Equity Index Futures (Micro) ── Exchange: CME
    "MES": 0.50,   # Micro E-mini S&P 500
    "MNQ": 0.50,   # Micro E-mini Nasdaq-100
    "MYM": 0.50,   # Micro E-mini Dow Jones
    "M2K": 0.50,   # Micro E-mini Russell 2000

    # ── Currency Futures ── Exchange: CME
    "6A": 2.40,    # Australian Dollar
    "6B": 2.40,    # British Pound
    "6C": 2.40,    # Canadian Dollar
    "6E": 2.40,    # Euro FX
    "6J": 2.40,    # Japanese Yen
    "6N": 2.40,    # New Zealand Dollar
    "6S": 2.40,    # Swiss Franc

    # ── Energy Futures ── Exchange: NYMEX
    "CL": 2.00,    # Crude Oil (WTI)
    "MCL": 0.50,   # Micro Crude Oil
    "NG": 2.00,    # Natural Gas
    "QG": 1.30,    # E-mini Natural Gas
    "QM": 2.00,    # E-mini Crude Oil
    "RB": None,    # RBOB Gasoline — NOT approved on Lucid
    "HO": None,    # Heating Oil — NOT approved on Lucid

    # ── Metals Futures ── Exchange: COMEX
    "GC": 3.00,    # Gold (full-size) — range reported $3.00–$5.60
    "MGC": 0.80,   # Micro Gold
    "SI": 3.00,    # Silver (full-size) — range reported $3.00–$5.60
    "HG": None,    # Copper — NOT confirmed as approved on Lucid
    "PL": None,    # Platinum — NOT confirmed as approved on Lucid

    # ── Agriculture (Grains) ── Exchange: CBOT
    "ZS": 2.80,    # Soybeans
    "ZC": 2.80,    # Corn
    "ZW": 2.80,    # Wheat
    "ZL": 2.80,    # Soybean Oil
    "ZM": 2.80,    # Soybean Meal

    # ── Livestock (Meats) ── Exchange: CME
    "LE": 2.80,    # Live Cattle
    "HE": 2.80,    # Lean Hogs

    # ── Fixed Income / Treasuries ── NOT approved on Lucid
    "ZN": None,    # 10-Year Treasury Note — NOT approved
    "ZT": None,    # 2-Year Treasury Note — NOT approved
    "ZB": None,    # 30-Year Treasury Bond — NOT approved
    "ZF": None,    # 5-Year Treasury Note — NOT approved

    # ── Crypto ── NOT approved on Lucid
    "BTC": None,   # Bitcoin — NOT approved
    "ETH": None,   # Ethereum — NOT approved

    # ── Other (International) ── Exchange: CME
    "NKD": 1.75,   # Nikkei 225 (USD-denominated)
}

# Contracts tracked in this project (from config.ASSETS) that are NOT available
# on Lucid Trading's approved product list.
NOT_AVAILABLE_ON_LUCID: list[str] = [
    symbol for symbol, commission in LUCID_COMMISSIONS.items()
    if commission is None
]

# Summary by asset class for quick reference.
COMMISSION_SUMMARY: dict[str, str] = {
    "Micro Contracts (MES, MNQ, MYM, M2K, MCL)": "$0.50 per side",
    "Micro Gold (MGC)": "$0.80 per side",
    "E-mini Natural Gas (QG)": "$1.30 per side",
    "E-mini Indices (ES, NQ, YM, RTY)": "$1.75 per side",
    "Energy Full-Size (CL, NG)": "$2.00 per side",
    "Currency Futures (6A–6S)": "$2.40 per side",
    "Agriculture & Livestock (ZS, ZC, ZW, ZL, ZM, LE, HE)": "$2.80 per side",
    "Metals Full-Size (GC, SI)": "$3.00–$5.60 per side",
}
