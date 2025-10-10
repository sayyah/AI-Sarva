# AI-Sarva: AI-Powered Crypto Trading Signals

AI-Sarva analyzes cryptocurrencies using technical indicators, news sentiment (via FinBERT), and generates trading signals (LONG/SHORT/HOLD) with entry/exit levels.

## Features
- Technical analysis (MA, RSI, MACD) via yfinance.
- News scraping and sentiment analysis from sources like CoinTelegraph.
- Trade calculations with volatility-based risk/reward.
- Modes: Single coin or find best across multiple.
- SQLite logging and reporting.
- CLI interface.

## Setup
1. Clone: `git clone https://github.com/sayyah/AI-Sarva.git`
2. Install: `pip install -r requirements.txt`
3. (Optional) Download FinBERT: Use Hugging Face model or local path.

## Usage
```bash
python src/main.py --coin BTC --portfolio 10000 --timeframe 4h --debug --report
