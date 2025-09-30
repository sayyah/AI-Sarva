import feedparser

RSS_FEEDS = {
    "Crypto - CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Crypto - CoinTelegraph": "https://cointelegraph.com/rss",
    "World - Reuters": "http://feeds.reuters.com/Reuters/worldNews",
    "World - BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Economy - MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Gold - Kitco": "https://www.kitco.com/rss/",
    "Tech - The Verge": "https://www.theverge.com/rss/index.xml",
    "Tech - TechCrunch": "https://techcrunch.com/feed/"
}


def find_news(num_results=5, keywords=None):
    all_articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:num_results]:
            title = entry.title
            link = entry.link
            if not keywords or any(k.lower() in title.lower() for k in keywords):
                all_articles.append(
                    {"source": source, "title": title, "url": link})
    return all_articles


if __name__ == "__main__":
    keywords = ["bitcoin", "crypto", "war", "peace",
                "election", "gold", "tax", "elon musk"]
    news = find_news(num_results=5, keywords=keywords)

    print("🔎 Found News:")
    for article in news:
        print(f"{article['source']} - {article['title']}\n{article['url']}\n")
