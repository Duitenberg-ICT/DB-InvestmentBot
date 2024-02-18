from datetime import datetime, timedelta, timezone
import feedparser
from roberta import polarity_scores
from processer import fetch_companies

url = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"
feed = feedparser.parse(url)

for entry in feed.entries:
    print("Entry Title:", entry.title)
    print("Semantics:", polarity_scores(entry.title))
    print("Companies:", fetch_companies(entry.title))
    print("Entry Published Date:", entry.published)
    print("\n")