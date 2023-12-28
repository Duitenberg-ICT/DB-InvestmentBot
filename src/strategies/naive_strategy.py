from datetime import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy


class MyStrategy(Strategy):
    def on_trading_iteration(self):
        if self.first_iteration:
            aapl_price = self.get_last_price("AAPL")
            quantity = self.portfolio_value // aapl_price
            order = self.create_order("AAPL", quantity, "buy")
            self.submit_order(order)

def run_backtest(start=datetime(2020, 11, 1, 0, 0, 0), 
                 end=datetime(2020, 12, 31, 0, 0, 0), 
                 budget=100000):
    MyStrategy.backtest(
        "strat_1",
        budget,
        YahooDataBacktesting,
        start,
        end,
    )