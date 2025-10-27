AI-Sarva: AI-Powered Crypto Trading Signals

AI-Sarva generates trading signals (LONG/SHORT/HOLD) for cryptocurrencies using technical indicators (MA, RSI, MACD) and news sentiment analysis (via FinBERT).

Features





Fetches real-time/historical data via yfinance.



Scrapes and analyzes news sentiment from CoinTelegraph, CoinDesk, etc.



Combines technical and sentiment signals for trade decisions.



Calculates entry/exit/stop levels based on volatility.



Modes: Single coin or find best across multiple coins.



Logs results to SQLite and JSON/CSV reports.



CLI interface with rich console output.

Setup





Clone: git clone https://github.com/sayyah/AI-Sarva.git



Install: pip install -r requirements.txt



(Optional) Set FinBERT path in .env or use Hugging Face model.



Create a .env file in the root directory with:

FINBERT_PATH=/path/to/local/finbert



Run: python src/main.py --coin BTC --portfolio 10000 --timeframe 4h --debug --report

Usage

python src/main.py --coin BTC --portfolio 10000 --timeframe 4h --debug --report
python src/main.py --portfolio 10000 --findbest

Output: Console tables, JSON reports in reports/, and SQLite data in data/sarva_data.db.

Project Structure





src/main.py: CLI entry point.



src/agents/: Agent classes for calculations, decisions, news, and technical analysis.



src/models/load_finbert.py: Loads FinBERT model.



src/utils/: Database and URL utilities.



reports/: Generated reports (JSON/CSV).



data/: SQLite database.

Development





Add tests in tests/.



Extend with backtesting (e.g., backtrader) or live alerts (e.g., Telegram).



Contribute via pull requests.

Disclaimer

For educational purposes only. Cryptocurrency trading is high-risk. Use at your own risk.
