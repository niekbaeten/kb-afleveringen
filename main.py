from datetime import datetime, timezone
import time

from jinja2 import Environment, PackageLoader, select_autoescape
import feedparser
import pytz

source = 'https://kleineboodschap.com/afleveringen?format=rss'

feed = feedparser.parse(source)
env = Environment(
    loader=PackageLoader("main"),
    autoescape=select_autoescape()
)

def time_struct_to_date_str(input):
	return time.strftime('%b %d, %Y', input)	
env.filters['time_struct_to_date_str'] = time_struct_to_date_str

template = env.get_template("episodes.html")
with open('kb.html', 'w', encoding='utf-8') as f:
	f.write(template.render(
		entries=feed.entries
	))
