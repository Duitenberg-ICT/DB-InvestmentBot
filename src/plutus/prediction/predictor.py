import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA


def predict(ticks, trim=500):
    results = dict()
    for tick in ticks:
        history = _load_history(tick, trim)
        model = ARIMA(history, order=(4, 1, 0))
        forecast = model.fit().forecast()
        results[tick] = forecast[0]
    return results


def _load_history(tick, trim):
    stock_info = yf.Ticker(tick)
    df = stock_info.history(period="max")
    if trim > 0:
        df = df.tail(trim)
    values = df['Close'].values
    history = [x for x in values]
    return history
