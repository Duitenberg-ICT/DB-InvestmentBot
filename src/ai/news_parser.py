import feedparser
import processer as p

f = feedparser.parse("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069")
example = f["entries"][0]["title"]

print(f)
print(example)
print(p.fetch_companies(example))