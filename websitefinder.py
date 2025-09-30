# websitefinder.py

class WebsiteFinder:
    def __init__(self, coin_name="BNB"):
        self.coin_name = coin_name.lower()
        # Predefined crypto news sites
        self.sources = [
            "https://cointelegraph.com",
            "https://www.investing.com",
            "https://decrypt.co",
            "https://cryptoslate.com",
            "https://newsbtc.com",
            "https://u.today"
        ]

    def find_websites(self):
        """Return a list of news sources related to crypto"""
        # For now, just return the predefined list
        # Later, you can extend this to fetch BNB-specific links
        return self.sources
