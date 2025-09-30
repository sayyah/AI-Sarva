from loadfinbertmodel import tokenizer, model  # GPTNeo
from newspaper import Article
from tradingagent import TradingAgent  # FinBERT


def summarize_article_with_llm(url):
    """Scrape article & summarize with GPTNeo"""
    article = Article(
        url, browser_user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
    article.download()
    article.parse()

    text = article.text

    # Summarize with GPTNeo
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, max_length=1024)
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7
    )
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary


def analyze_news(url, portfolio_value=1000):
    """Pipeline: Summarize news & make trading decision"""
    summary = summarize_article_with_llm(url)

    # Use TradingAgent (FinBERT) for decision
    agent = TradingAgent()
    decision = agent.trading_decision(summary, portfolio_value)

    return {"summary": summary, "decision": decision}


# Example usage
if __name__ == "__main__":
    url = "https://cointelegraph.com/news/bitcoin-price-today"
    result = analyze_news(url, portfolio_value=2000)
    print("📄 Summary:\n", result["summary"])
    print("\n📊 Trading Decision:\n", result["decision"])
