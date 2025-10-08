import yfinance as yf


class ChartAgent:
    def __init__(self, coin, timeframe="4h", debug=False):
        self.coin = coin.upper()
        self.timeframe = timeframe
        self.debug = debug

    def analyze_chart(self):
        try:
            ticker = f"{self.coin}-USD"
            data = yf.download(ticker, period="30d", interval=self.timeframe)
            if data.empty:
                print(f"⚠️ No chart data for {ticker}")
                return "NEUTRAL", self.timeframe

            close = data['Close']
            ma_short = close.rolling(5).mean()
            ma_long = close.rolling(20).mean()

            bias = "BULLISH" if ma_short.iloc[-1] > ma_long.iloc[-1] else "BEARISH"

            if self.debug:
                print(
                    f"📊 Chart bias ({self.timeframe}): {bias} — MA5={ma_short.iloc[-1]:.2f}, MA20={ma_long.iloc[-1]:.2f}")

            return bias, self.timeframe
        except Exception as e:
            print(f"⚠️ Chart analysis failed for {self.coin}: {e}")
            return "NEUTRAL", self.timeframe
