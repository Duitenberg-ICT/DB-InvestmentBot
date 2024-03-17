import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from pandas.plotting import lag_plot
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
import yfinance as yf


class Predictor:
    def __init__(self, ticker: str, period="3y"):
        self.ticker = ticker
        self.data = yf.download(ticker, period=period)

    def plot(self):
        figure(num=None, figsize=(8, 6), dpi=80, facecolor="w", edgecolor="k")
        self.data["Close"].plot()
        plt.show()

    def lag_plot(self):
        figure(num=None, figsize=(8, 6), dpi=80, facecolor="w", edgecolor="k")
        lag_plot(self.data["Close"], lag=5)
        plt.show()

    def overview(self):
        return self.data.describe()

    def predict(self, verbose=False):
        x_train = self.data["Close"].values
        history = [x for x in x_train]
        model = ARIMA(history, order=(4, 1, 0))
        model_fit = model.fit()
        output = model_fit.get_forecast()
        ci = output.conf_int(0.05)

        metadata = dict()
        metadata["PP"] = output.predicted_mean[0]
        metadata["SE"] = output.se_mean[0]
        metadata["CI"] = [ci[0, 0], ci[0, 1]]
        if verbose:
            print("Predicted price (" + self.ticker + "):", round(metadata["PP"], 2), "USD")
            print("Standard error:", round(metadata["SE"], 4))
            print("95% CI: (", round(metadata["CI"][0], 2), round(metadata["CI"][1], 2), ")")
        return metadata

    def long_predict(self, days: int = 365, verbose: bool = False):
        df = self._prepare_dataset()
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        if verbose:
            model.plot(forecast)
            plt.title("Prediction of the " + self.ticker +
                      " Stock Price" + " (" + str(days) + " days)")
            plt.xlabel("Date")
            plt.ylabel("Close Stock Price")
            plt.show()
            model.plot_components(forecast)
            plt.show()
        return forecast

    def _prepare_dataset(self):
        df = self.data.reset_index()
        df = df[["Date", "Close"]]
        df = df.rename(columns={"Date": "ds", "Close": "y"})
        df["ds"] = df["ds"].dt.tz_localize(None)
        return df
