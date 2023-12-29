from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy


class NaiveStrategy(Strategy):

    def initialize(self, sleeptime="10M", minutes_before_closing=15):
        self.sleeptime = sleeptime
        self.minutes_before_closing = minutes_before_closing

    def on_trading_iteration(self):
        if self.first_iteration:
            aapl_price = self.get_last_price("AAPL")
            quantity = self.portfolio_value // aapl_price
            order = self.create_order("AAPL", quantity, "buy")
            self.submit_order(order)

    def after_market_closes(self):
        self.log_message("MARKET CLOSED")
        self.log_message(f"TOTAL PORTFOLIO VALUE: {self.portfolio_value}")
        self.log_message(f"AMOUNT OF CASH: {self.cash}")


backtesting_start = datetime(2020, 1, 1)
backtesting_end = datetime(2020, 12, 31)
NaiveStrategy.backtest(
    YahooDataBacktesting,
    backtesting_start,
    backtesting_end,
)
