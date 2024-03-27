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
        info = []
        try:
            eps = self.info["trailingEps"]
        except KeyError:
            eps = None
        info.append(eps)

        try:
            cps = self.info["operatingCashflow"] / self.info["sharesOutstanding"]
        except KeyError:
            cps = None
        info.append(cps)

        try:
            dps = self.info["dividendRate"]
        except KeyError:
            dps = None
        info.append(dps)

        try:
            eg = self.info["earningsGrowth"]
        except KeyError:
            eg = None
        info.append(eg)

        try:
            pr = self.info["beta"]
        except KeyError:
            pr = None
        info.append(pr)

        df[self.name] = info
        df.rename(index={0: "EPS", 1: "CPS", 2: "DPS", 3: "EG", 4: "PR"}, inplace=True)
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
