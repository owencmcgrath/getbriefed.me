import yfinance as yf


def get_stock_prices(symbols=['SPY', 'QQQ', 'VTI']):
    try:
        stocks = []
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2d')

            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change = ((current - previous) / previous) * 100

                stocks.append({
                    'symbol': symbol,
                    'price': f"${current:.2f}",
                    'change': f"{change:+.2f}%"
                })

        return stocks

    except Exception as e:
        print(f"Stock error: {e}")
        return []
