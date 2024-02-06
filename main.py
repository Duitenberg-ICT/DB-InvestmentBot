import yfinance as yf
import datetime


if __name__ == "__main__":
    
    tickers = ['AAPL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'MSFT', 'ORCL', 'AMD', 'INTC']
    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2023, 12, 31)

    for ticker in tickers:
        price_data = yf.download(tickers=ticker, period="5d", interval="15m")
        # filtered = price_data[start: end]["Close"].tolist()
        # print(filtered)
