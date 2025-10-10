# databaseagent.py
import sqlite3
from datetime import datetime


class DatabaseAgent:
    def __init__(self, db_path="sarva_news.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS news_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT,
            url TEXT,
            date TEXT,
            sentiment TEXT,
            action TEXT,
            confidence REAL,
            amount REAL,
            entry_price REAL,
            exit_price REAL,
            stop_loss REAL,
            tech_bias TEXT,
            timeframe TEXT,
            text_length INTEGER,
            summary TEXT
        )''')
        conn.commit()
        conn.close()

    def save_analysis(self, coin, url, decision, sentiment, tech_bias, timeframe, text):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''INSERT INTO news_analysis 
            (coin, url, date, sentiment, action, confidence, amount, entry_price, exit_price, stop_loss, 
             tech_bias, timeframe, text_length, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            coin.upper(),
            url,
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            sentiment,
            decision.get("action"),
            decision.get("confidence"),
            decision.get("amount"),
            decision.get("entry_price"),
            decision.get("exit_price"),
            decision.get("stop_loss"),
            tech_bias,
            timeframe,
            len(text),
            text[:300]  # short preview
        ))
        conn.commit()
        conn.close()

    def query_report(self, coin=None, sentiment=None, start_date=None, end_date=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        query = "SELECT date, coin, sentiment, action, confidence, url FROM news_analysis WHERE 1=1"
        params = []

        if coin:
            query += " AND coin = ?"
            params.append(coin.upper())

        if sentiment:
            query += " AND sentiment = ?"
            params.append(sentiment.upper())

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC"

        c.execute(query, params)
        results = c.fetchall()
        conn.close()
        return results
