import warnings
import yfinance as yf
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA


def predict(df, order=(4, 1, 0)):
    train_data, test_data = (
        df[int((len(df) * 0.7) * 0.5):int(len(df) * 0.7)], df[int(len(df) * 0.7):])
    training_data = train_data['Close'].values
    test_data = test_data['Close'].values
    history = [x for x in training_data]

    model_predictions = []
    n_test_observations = len(test_data)
    for time_point in range(n_test_observations):
        model = ARIMA(history, order=order)
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = output[0]
        model_predictions.append(yhat)
        true_test_value = test_data[time_point]
        history.append(true_test_value)

    mse_error = mean_squared_error(test_data, model_predictions)
    print('Mean Squared Error: {}'.format(mse_error))
    return model_predictions


def get_tick_data(tick_name, trim=365):
    stock_info = yf.Ticker(tick_name)
    df = stock_info.history(period="max")
    if trim > 0:
        df = df.tail(trim)
    return df
