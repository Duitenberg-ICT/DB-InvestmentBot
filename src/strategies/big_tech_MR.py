import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
import pandas as pd


class MeanReversion_tech(Strategy):
    def initialize(self):
        self.sleeptime = "1D"
        self.symbols = self.get_sp500_symbols()
        self.big_players = ['AAPL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'MSFT', 'ORCL', 'AMD', 'INTC']

    def get_sp500_symbols(self):
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        symbols = df['Symbol'].tolist()
        # Some symbols use a different format in Yahoo Finance
        symbols = [symbol.replace('.', '-') for symbol in symbols]
        return symbols

    def on_trading_iteration(self):
        cash_available = self.cash
        per_stock_allocation = cash_available / len(self.big_players)

        for ticker in self.big_players:
            bars = self.get_historical_prices(ticker, 30, "day")
            prices = bars.df['close'].values
            mean = prices.mean()
            std_dev = prices.std()
            latest_close = prices[-1]

            print("cash available: " + str(cash_available))

            if latest_close > mean + std_dev and self.get_position(ticker) is not None:
                order = self.create_order(ticker, self.get_position(ticker).quantity, 'sell')
                self.submit_order(order)
                print('selling ' + str(self.get_position(ticker).quantity) + ' shares of ' + ticker + ' for ' + str(latest_close))
            elif latest_close < mean - std_dev:
                if per_stock_allocation >= self.get_last_price(ticker):
                    order = self.create_order(ticker, per_stock_allocation // self.get_last_price(ticker), 'buy')
                    self.submit_order(order)
                    print('buying ' + str(per_stock_allocation // self.get_last_price(ticker)) + ' shares of ' + ticker + ' for ' + str(
                        self.get_last_price(ticker)))

    def on_backtest_end(self):
        self.log_returns()


backtesting_start = datetime.datetime(2020, 1, 1)
backtesting_end = datetime.datetime(2023, 12, 31)
MeanReversion_tech.backtest(
    YahooDataBacktesting,
    backtesting_start,
    backtesting_end,
)