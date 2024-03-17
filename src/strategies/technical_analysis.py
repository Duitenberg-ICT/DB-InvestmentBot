from datetime import datetime, timedelta
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
import requests
import pandas as pd
import yfinance as yf


def get_snp_tickers():
    url = ('https://www.ssga.com/us/en/intermediary/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us'
           '-en-spy.xlsx')
    df = pd.read_excel(url, engine='openpyxl', index_col='Ticker', skiprows=4).dropna()
    tickers = df.index.tolist()
    return [item.replace('.', '-') for item in tickers]


class TAnalysis(Strategy):
    def initialize(self, **kwargs):
        self.sleeptime = "1D"
        self.portfolio = []
        self.snp500 = get_snp_tickers()
        self.buys = []
        self.sells = [] # sell 50%
        self.strong_sells = [] # sell all
        self.ratings = {}
        self.indicators = []
        self.max_holdings = 7 # maximum ten different tickers in portfolio
        self.mag_7 = ['AAPL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'MSFT']
        # self.big_finance = ['BRK-B', 'JPM', 'V', 'MA', 'BAC', 'GS', 'WFC', 'C', 'AXP', 'PYPL']
        # self.big_natural_resources = ['XOM', 'CVX', 'COP', 'LIN', 'EOG', 'NEE', 'GE', 'DUK', 'SLB', 'SO']
        # self.big_health = ['LLY', 'JNJ', 'ABBV', 'PFE', 'AMGN', 'MRK', 'BMY', 'GILD', 'UNH', 'ABT']
        self.big_consumer = ['AVGO', 'HD', 'MCD', 'BKNG', 'NKE', 'KO', 'PG', 'WMT', 'COST', 'PEP']

    def daily_analysis(self):
        self.ratings.clear()
        self.buys.clear()
        self.sells.clear()
        self.strong_sells.clear()
        self.portfolio.clear()
        positions = self.get_positions()
        for position in positions:
            # Show the quantity of each position
            print(position.quantity)
            # Show the asset of each position
            print(position.asset)
            self.portfolio.append(str(position.asset))
        # -----------------------------------------------------
        # scoring process (MA:25%, BB:25%, RSI:25%, MACD:25%)
        # todo also integrate ARIMA to scoring process in the future
        # todo Step 1: calculate technical indicators
        for ticker in self.mag_7:
            bars = self.get_historical_prices(ticker, 30, "day")
            prices = bars.df['close'].values
            indicators = self.calculate_indicators(ticker, prices)

        # todo Step 2: compute scores for each indicator (FOR THE FUTURE: FINE TUNE EVALUATION ALGORITHM)
            score_ma = self.score_ma(indicators['ma5'], indicators['ma10'], indicators['ma20'], indicators['ma30'], prices[-1])
            score_bb = self.score_bb(prices[-1], indicators['LBB'], indicators['MBB'], indicators['UBB'])
            score_rsi = self.score_rsi(indicators['RSI'])
            score_macd = self.score_macd(indicators['MACD'], indicators['MACD_signal'])

        # todo Step 3: compute overall rating
            rating = int(0.3 * score_ma + 0.2 * score_bb + 0.2 * score_rsi + 0.3 * score_macd)
            print('Ticker: ' + ticker + ' score: ' + str(rating))

        # todo Step 4: add score to list
            self.ratings[ticker] = rating

        # todo Step 5: Get top three rated stocks of the day, put them into the buy list if the score is above 80 (strong buy)
        sorted_ratings = sorted(self.ratings.items(), key=lambda item: item[1], reverse=True)[:3]

        for ticker in sorted_ratings:
            if ticker[1] >= 60:
                print('Buying ticker: ' + ticker[0])
                self.buys.append(ticker[0])

        # -----------------------------------------------------
        # look for exits
        # todo Step 1: If the score of any of the tickers in portfolio falls below a certain level, sell accordingly
        print(self.get_positions())
        for ticker in self.portfolio:
            if ticker != 'USD':
                if 30 <= self.ratings[ticker] <= 40:
                    print('Selling partially ticker: ' + ticker)
                    self.sells.append(ticker)
                if self.ratings[ticker] <= 20:
                    print('Selling ticker: ' + ticker)
                    self.strong_sells.append(ticker)


    def calculate_indicators(self, ticker, prices):
        # calculate 5-day, 10-day, 20-day & 30-day moving averages
        ticker_indicators = {'ma5': prices[-5:].mean(), 'ma10': prices[-10:].mean(), 'ma20': prices[-20:].mean(),
                             'ma30': prices.mean()}

        # calculate lower, middle and upper bollinger bands
        ticker_indicators['UBB'] = ticker_indicators['ma20'] + 2 * prices[-20:].std()
        ticker_indicators['LBB'] = ticker_indicators['ma20'] - 2 * prices[-20:].std()
        ticker_indicators['MBB'] = ticker_indicators['ma20']

        # calculate relative strength index (RSI)
        ticker_indicators['RSI'] = self.RSI(ticker)

        # calculate Moving average convergence/divergence (MACD)
        ticker_indicators['MACD'], ticker_indicators['MACD_signal'] = self.MACD(ticker)

        return ticker_indicators


    def RSI(self, ticker, window=14):
        # Define the end date as today
        end_date = datetime.today().strftime('%Y-%m-%d')

        # Define the start date as 14 trading days before the end date
        start_date = (datetime.today() - timedelta(days=18)).strftime('%Y-%m-%d')

        # Download the necessary historical data
        data = yf.download(ticker, start=start_date, end=end_date)

        delta = data['Close'].diff()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the EWMA (Exponential Weighted Moving Average)
        roll_up1 = up.ewm(span=window).mean()
        roll_down1 = down.abs().ewm(span=window).mean()

        # Calculate the RSI based on EWMA
        RS = roll_up1 / roll_down1
        RSI = 100.0 - (100.0 / (1.0 + RS))

        return RSI.iloc[-1]


    def MACD(self, ticker):
        # Define the end date as today
        end_date = datetime.today().strftime('%Y-%m-%d')

        # Define the start date as 14 trading days before the end date
        start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

        # Download historical data for desired ticker symbol
        data = yf.download(ticker, start_date, end_date)

        # Calculate the Short Term Exponential Moving Average
        ShortEMA = data.Close.ewm(span=12, adjust=False).mean()  # 12 period span

        # Calculate the Long Term Exponential Moving Average
        LongEMA = data.Close.ewm(span=26, adjust=False).mean()  # 26 period span

        # Calculate the Moving Average Convergence/Divergence (MACD)
        MACD = ShortEMA - LongEMA

        # Calculate the signal line
        signal = MACD.ewm(span=9, adjust=False).mean()

        return MACD.iloc[-1], signal.iloc[-1]


    # give a score for the current moving averages trend out of 100
    def score_ma(self, ma5, ma10, ma20, ma30, price):
        score = 0
        if price < ma10 and price < ma20 and price < ma30:
            return 0
        if ma5 > ma10:
            score += 25
            if ma5 > ma20:
                score += 25
                if ma5 > ma30:
                    score += 50
        return score


    # give a score for current price against bollinger bands. Out of 100
    def score_bb(self, price, LBB, MBB, UBB):
        if price > UBB:
            return 0
        if price <= UBB and price >= MBB:
            return 25
        if price <= MBB and price >= LBB:
            return 50
        if price < LBB:
            return 100



    # give a score for current rsi. Out of 100
    def score_rsi(self, rsi):
        if rsi >= 70:
            return 0
        if rsi < 70 and rsi >= 30:
            return 50
        if rsi < 30:
            return 100


    # give a score for current macd. Out of 100
    def score_macd(self, macd, signal):
        score = 0
        if macd > 0:
            score += 50
        if macd > signal:
            score += 50
        return score


    def before_starting_trading(self):
        self.daily_analysis()
        print(self.buys)
        print(self.sells)
        print(self.strong_sells)


    def on_trading_iteration(self):
        cash_available = self.cash
        per_stock_allocation = cash_available / self.max_holdings

        for ticker in list(set(self.buys)):
            quantity = per_stock_allocation // self.get_last_price(ticker)
            if quantity > 0:
                order = self.create_order(ticker, quantity, 'buy')
                self.submit_order(order)
                print('buying ' + str(per_stock_allocation // self.get_last_price(ticker)) + ' shares of ' + ticker + ' for ' + str(self.get_last_price(ticker)))
                print("cash available: " + str(cash_available))
                self.portfolio.append(ticker)
            self.buys.remove(ticker)

        for ticker in list(set(self.sells)):
            print('selling ticker: ' + ticker)
            quantity = self.get_position(ticker).quantity // 2
            if quantity > 0:
                order = self.create_order(ticker, quantity, 'sell')
                self.submit_order(order)
                print('selling ' + str(self.get_position(ticker).quantity // 2) + ' shares of ' + ticker + ' for ' + str(self.get_last_price(ticker)))
                print("cash available: " + str(cash_available))
            else:
                order = self.create_order(ticker, self.get_position(ticker).quantity, 'sell')
                self.submit_order(order)
                print('selling ' + str(self.get_position(ticker).quantity) + ' shares of ' + ticker + ' for ' + str(
                    self.get_last_price(ticker)))
                print("cash available: " + str(cash_available))
                self.portfolio.remove(ticker)
            self.sells.remove(ticker)

        for ticker in list(set(self.strong_sells)):
            order = self.create_order(ticker, self.get_position(ticker).quantity, 'sell')
            self.submit_order(order)
            print('selling ' + str(self.get_position(ticker).quantity) + ' shares of ' + ticker + ' for ' + str(self.get_last_price(ticker)))
            print("cash available: " + str(cash_available))
            self.portfolio.remove(ticker)
            self.strong_sells.remove(ticker)

    def on_backtest_end(self):
        self.log_returns()


backtesting_start = datetime(2021, 3, 1)
backtesting_end = datetime(2024, 3, 1)
TAnalysis.backtest(
    YahooDataBacktesting,
    backtesting_start,
    backtesting_end,
)
