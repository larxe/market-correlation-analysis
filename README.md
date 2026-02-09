# Market Correlation Analysis

![App Preview](preview.png)

A professional Python-based tool to analyze correlations between various financial markets (Currencies, Fixed Income, Commodities, Cryptocurrencies, and Indices) using real-time data from Yahoo Finance.

## 🚀 Features

- **Multi-Market:** Monitors over 30 key financial assets.
- **Dual Time Horizon:** Compare short-term (15 days) vs. medium-term (3 months) correlations.
- **Difference Analysis:** Visualize how relationships between assets are evolving (converging or diverging).
- **Strong Correlation Filter:** Automatically identifies "Twin" or "Mirror" assets for hedging or diversification strategies.
- **Native Interface:** Designed for seamless visual integration with Windows.
- **Export:** Save heatmaps as high-resolution images (.png).

## 🛠️ Installation

### Executable Version (Recommended)
1. Go to the `dist/` folder.
2. Run `Analisis_Correlaciones.exe`.
*Does not require Python to be installed.*

### Development Version
If you prefer to run the source code:
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install yfinance pandas seaborn matplotlib numpy
   ```
3. Run the script:
   ```bash
   python "corelación entre mercados.py"
   ```

## 📊 Strategy Guide
- **Correlation > 0.80:** Assets move almost identically. Risk of doubling exposure.
- **Correlation < -0.80:** Assets move in opposite directions. Ideal for hedging.
- **Correlation near 0:** Independent assets. Ideal for true portfolio diversification.

---
Developed for technical and quantitative analysis of global markets.