import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import pandas as pd
from pandas.plotting import lag_plot
import yfinance as yf


class BelfortTicker(yf.Ticker):
    """
    BelfortTicker is a subclass of yfinance.Ticker that adds some functionalities to the stock data such as
    plotting the history of the stock price and lag plot, and getting the fundamental ratios of the stock.
    """

    def __init__(self, name: str, period: str):
        super().__init__(name)
        self.name = name
        self.period = period
        self.data = yf.download(name, period=period)
        self.predicted = None
        self.predicted_long = None

    def get_ratios(self):
        """
        Get the fundamental ratios of the stock:
        - EPS: Earnings per share
        - CPS: Cash flow per share
        - DPS: Dividend per share
        - EG: Earnings growth
        - PR: Perceived risk of the stock
        :return: dataframe of ratios
        """
        df = pd.DataFrame()
        info = {
            "trailingEps": "EPS",
            "operatingCashflow": "CPS",
            "dividendRate": "DPS",
            "earningsGrowth": "EG",
            "beta": "PR"
        }
        for key, col_name in info.items():
            try:
                value = self.info[key]
            except KeyError:
                value = None
            df[col_name] = [value]
        return df

    def plot_history(self):
        """
        Plot the history of the stock price.
        """
        figure(num=None, figsize=(8, 6), dpi=80, facecolor="w", edgecolor="k")
        self.data["Close"].plot()
        plt.title("History of the " + self.name + " Stock Price " + "for the last " + self.period)
        plt.grid()
        plt.show()

    def lag_plot_history(self, lag=5):
        """
        Plot the lag plot of the stock price.
        """
        figure(num=None, figsize=(8, 6), dpi=80, facecolor="w", edgecolor="k")
        lag_plot(self.data["Close"], lag=lag)
        plt.title("Lag plot of the " + self.name + " Stock Price " + "with lag=" + str(lag))
        plt.grid()
        plt.show()
