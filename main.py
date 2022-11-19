import locale
from operator import itemgetter
import time

from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2.ext import Markup
import feedparser
import json

def main():
	locale.setlocale(locale.LC_ALL,'nl_NL.UTF-8')

	source = 'https://kleineboodschap.com/afleveringen?format=rss'

	feed = feedparser.parse(source)
	env = Environment(
		loader=PackageLoader("main"),
		autoescape=select_autoescape()
	)

	def handle_summary_and_show_notes(entry):
		summary = entry.summary
		show_notes = []
		if 'Show notes' in summary:
			summary, notes = summary.split('<strong>Show notes</strong>')
			soup = BeautifulSoup(notes, features="html.parser")
			for a in soup.find_all('a', href=True):
				show_notes.append({'text': a.contents[0], 'link': a['href']})
		return Markup(summary).striptags(), show_notes

	def handle_duration(entry):
		# episode 266 has itunes_season tag instead of itunes_duration
		if hasattr(entry, 'itunes_season'):
			value = entry.itunes_season
		else:
			value = entry.itunes_duration
		# force leading zeros which are missing sometime
		time_struct = time.strptime(value, '%H:%M:%S')
		return time.strftime('%H:%M:%S', time_struct)

	with open('episodes.json', 'r') as f:
		episodes = json.load(f)

	for entry in feed.entries:
		if any(episode['id'] == int(entry.itunes_episode) for episode in episodes):
			# if the episode is already in the json, don't touch it
			continue

		summary, show_notes = handle_summary_and_show_notes(entry)

		episodes.append({
			"id": int(entry.itunes_episode),
			"link": entry.link,
			"title": entry.itunes_title,
			"subtitle": entry.subtitle,
			"published": time.strftime('%A, %d %B %Y', entry.published_parsed),
			"tags": [tag.term for tag in entry.tags],
			"summary": summary,
			"show_notes": show_notes,
			"duration": handle_duration(entry),
			"media_url": entry.media_content[0]['url']
		})

	episodes = sorted(episodes, key=itemgetter('id'), reverse=True)

	with open('episodes.json', 'w') as f:
		json.dump(episodes, f, indent=2)

	template = env.get_template("episodes.html")
	with open('index.html', 'w', encoding='utf-8') as f:
		f.write(template.render(
			entries=episodes
		))

if __name__ == "__main__":
	main()
