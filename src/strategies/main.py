from datetime import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy


# A simple strategy that buys AAPL on the first day and hold it
class MyStrategy(Strategy):
    def on_trading_iteration(self):
        if self.first_iteration:
            aapl_price = self.get_last_price("AAPL")
            quantity = self.portfolio_value // aapl_price
            order = self.create_order("AAPL", quantity, "buy")
            self.submit_order(order)


# Pick the dates that you want to start and end your backtest
# and the allocated budget
backtesting_start = datetime(2020, 11, 1, 0, 0, 0)
backtesting_end = datetime(2020, 12, 31, 0, 0, 0)
budget = 100000

# Run the backtest
MyStrategy.backtest(
    "strat_1",
        budget,
        YahooDataBacktesting,
        backtesting_start,
        backtesting_end,
)
