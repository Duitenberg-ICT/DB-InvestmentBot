import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
import yfinance as yf
import pandas as pd


class Benchmark(Strategy):
    def initialize(self, symbol=""):
        # Will make on_trading_iteration() run every 180 minutes
        self.sleeptime = "1D"
        self.sp500_symbols = self.get_sp500_symbols()


    def get_sp500_symbols(self):
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        symbols = df['Symbol'].tolist()
        # Some symbols use a different format in Yahoo Finance
        symbols = [symbol.replace('.', '-') for symbol in symbols]
        return symbols

    def on_trading_iteration(self):
        if self.first_iteration:
            for symbol in self.sp500_symbols:
                if self.get_last_price(symbol) is not None:
                    order = self.create_order(symbol, 1, 'buy')
                    self.submit_order(order)


backtesting_start = datetime.datetime(2023, 2, 1)
backtesting_end = datetime.datetime(2024, 2, 1)
Benchmark.backtest(
    YahooDataBacktesting,
    backtesting_start,
    backtesting_end
)