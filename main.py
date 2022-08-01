import time

from jinja2 import Environment, PackageLoader, select_autoescape
import feedparser

source = 'https://kleineboodschap.com/afleveringen?format=rss'

feed = feedparser.parse(source)
env = Environment(
    loader=PackageLoader("main"),
    autoescape=select_autoescape()
)

def time_struct_to_date_str(input):
	return time.strftime('%b %d, %Y', input)	
env.filters['time_struct_to_date_str'] = time_struct_to_date_str

def check_duration_format(input):
	# force leading zeros which are missing sometime
	time_struct = time.strptime(input, '%H:%M:%S')
	return time.strftime('%H:%M:%S', time_struct)
env.filters['check_duration_format'] = check_duration_format

template = env.get_template("episodes.html")
with open('index.html', 'w', encoding='utf-8') as f:
	f.write(template.render(
		entries=feed.entries
	))
