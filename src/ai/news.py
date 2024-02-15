class News:

    def __init__(self, timedate=None, companies=None, text=None, sentiment=None):
        self.timedate = timedate
        self.companies = companies
        self.text = text
        self.sentiment = sentiment

    def add_timedate(self, timedate):
        self.timedate = timedate

    def add_companies(self, companies):
        self.companies = companies

    def add_text(self, text):
        self.text = text

    def add_sentiment(self, sentiment_scores):
        self.sentiment = max(sentiment_scores, key=sentiment_scores.get)

    def __str__(self):
        return f"Piece(timedate={self.timedate}, companies={self.companies}, text={self.text}, sentiment={self.sentiment})"
