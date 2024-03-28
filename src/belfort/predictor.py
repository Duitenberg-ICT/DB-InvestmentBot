import matplotlib.pyplot as plt
import pandas as pd
from prophet import Prophet
from src import BelfortTicker
from statsmodels.tsa.arima.model import ARIMA


def predict(tickers: [BelfortTicker]):
    """
    Predict the stock price of the tickers using ARIMA model for the next day.
    :param tickers: tickers to predict of type BelfortTicker.
    :return: a dataframe with predictions, standard error and confidence interval.
    """
    df = pd.DataFrame()
    for ticker in tickers:
        x_train = ticker.data["Close"].values
        history = [x for x in x_train]
        model = ARIMA(history, order=(4, 1, 0))
        model_fit = model.fit()
        output = model_fit.get_forecast()
        ci = output.conf_int(0.05)
        df[ticker.name] = [output.predicted_mean[0], output.se_mean[0], (ci[0, 0], ci[0, 1])]
    df.rename(index={0: "PP", 1: "SE", 2: "CI"}, inplace=True)
    return df


def long_predict(tickers: [BelfortTicker], days: int = 365, verbose: bool = False):
    """
    Predict the stock price of the ticker using Prophet model for the next days.
    :param tickers: tickers to predict of type BelfortTicker.
    :param days: days since today to predict.
    :param verbose: if True, plot the prediction graph and the components.
    :return: a dataframe with predictions.
    """
    forecasts = dict()

    for ticker in tickers:
        df = _prepare_dataset(ticker)
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        forecasts[ticker.name] = forecast
        if verbose:
            model.plot(forecast)
            plt.title("Prediction of the " + ticker.name +
                      " Stock Price" + " (" + str(days) + " days)")
            plt.xlabel("Date")
            plt.ylabel("Close Stock Price")
            plt.show()
            model.plot_components(forecast)
            plt.show()

    return forecasts


def _prepare_dataset(ticker: BelfortTicker):
    """
    Only for internal use. Prepare the dataset for the Prophet model.
    :param ticker: ticker to predict of type BelfortTicker.
    :return: a dataframe with renamed columns.
    """
    df = ticker.data.reset_index()
    df = df[["Date", "Close"]]
    df = df.rename(columns={"Date": "ds", "Close": "y"})
    df["ds"] = df["ds"].dt.tz_localize(None)
    return df
