import locale
import time

from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape
import feedparser

locale.setlocale(locale.LC_ALL,'nl_NL.UTF-8')

source = 'https://kleineboodschap.com/afleveringen?format=rss'

feed = feedparser.parse(source)
env = Environment(
    loader=PackageLoader("main"),
    autoescape=select_autoescape()
)

def time_struct_to_date_str(input):
	return time.strftime('%A, %d %B %Y', input)	
env.filters['time_struct_to_date_str'] = time_struct_to_date_str

def check_duration_format(input):
	# force leading zeros which are missing sometime
	time_struct = time.strptime(input, '%H:%M:%S')
	return time.strftime('%H:%M:%S', time_struct)
env.filters['check_duration_format'] = check_duration_format

for entry in feed.entries:
	entry.show_notes = []
	if 'Show notes' in entry.summary:
		entry.summary, show_notes = entry.summary.split('<strong>Show notes</strong>')
		soup = BeautifulSoup(show_notes, features="html.parser")
		for a in soup.find_all('a', href=True):
			entry.show_notes.append({'text': a.contents[0], 'link': a['href']})

template = env.get_template("episodes.html")
with open('index.html', 'w', encoding='utf-8') as f:
	f.write(template.render(
		entries=feed.entries
	))
