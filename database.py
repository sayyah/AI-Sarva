# database.py
import sqlite3
from datetime import datetime
import os
import pandas as pd

DB_FILE = "sarva_data.db"


class Database:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        # News
        c.execute("""
        CREATE TABLE IF NOT EXISTS news_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            coin TEXT,
            url TEXT,
            sentiment TEXT,
            confidence REAL,
            action TEXT,
            amount REAL,
            source TEXT,
            text_excerpt TEXT
        )
        """)
        # Technical
        c.execute("""
        CREATE TABLE IF NOT EXISTS technical_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            coin TEXT,
            timeframe TEXT,
            bias TEXT,
            strength REAL,
            reason TEXT
        )
        """)
        self.conn.commit()

    def save_news(self, coin, url, sentiment, confidence, action, amount, text_excerpt, source="auto"):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO news_analysis (date, coin, url, sentiment, confidence, action, amount, source, text_excerpt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            coin.upper(),
            url,
            sentiment,
            confidence,
            action,
            amount,
            source,
            text_excerpt[:500]
        ))
        self.conn.commit()

    def save_technical(self, coin, timeframe, bias, strength, reason):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO technical_analysis (date, coin, timeframe, bias, strength, reason)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            coin.upper(),
            timeframe,
            bias,
            strength,
            reason
        ))
        self.conn.commit()

    # ----------- REPORTING FUNCTIONS -----------

    def get_news_summary(self):
        df = pd.read_sql_query(
            "SELECT coin, sentiment, COUNT(*) as count FROM news_analysis GROUP BY coin, sentiment", self.conn)
        if df.empty:
            return "No news data yet."
        summary = "\n📰 News Summary:\n"
        for coin in df["coin"].unique():
            summary += f"\n{coin}:\n"
            sub = df[df["coin"] == coin]
            for _, row in sub.iterrows():
                summary += f"   {row['sentiment']}: {int(row['count'])}\n"
        return summary

    def get_technical_summary(self):
        df = pd.read_sql_query("""
            SELECT coin, bias, AVG(strength) as avg_strength, MAX(date) as last_update
            FROM technical_analysis
            GROUP BY coin, bias
            ORDER BY last_update DESC
        """, self.conn)
        if df.empty:
            return "No technical data yet."
        summary = "\n📊 Technical Summary:\n"
        for _, row in df.iterrows():
            summary += f"   {row['coin']} → {row['bias']} (avg strength {row['avg_strength']:.2f}) [Last: {row['last_update'][:19]}]\n"
        return summary

    def get_best_coins(self):
        df_news = pd.read_sql_query("""
            SELECT coin,
                   SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END) as good,
                   SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) as bad
            FROM news_analysis GROUP BY coin
        """, self.conn)

        df_tech = pd.read_sql_query("""
            SELECT coin, bias, AVG(strength) as strength FROM technical_analysis GROUP BY coin, bias
        """, self.conn)

        if df_news.empty and df_tech.empty:
            return "⚠️ Not enough data to find best coins."

        df = pd.merge(df_news, df_tech, on="coin", how="outer").fillna(0)

        df["score"] = (df["good"] - df["bad"]) + (df["strength"] *
                                                  (df["bias"].apply(lambda x: 1 if x == "BULLISH" else -1)))
        df = df.sort_values("score", ascending=False)

        summary = "\n💡 Best Coins to Trade (based on sentiment + tech):\n"
        for _, row in df.iterrows():
            summary += f"   {row['coin']}: {row['score']:.2f} ({row['bias']}, {row['strength']:.2f})\n"
        return summary

    def generate_report(self):
        report = f"📅 Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        report += self.get_news_summary()
        report += self.get_technical_summary()
        report += self.get_best_coins()
        return report
