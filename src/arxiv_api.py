import requests
import feedparser


def access_arxiv_api():
  # Access the arXiv API
  base_url = 'http://export.arxiv.org/api/query?'
  search_query = 'search_query=all:electron'
  start = 0
  max_results = 10
  sort_by = 'submittedDate'
  sort_order = 'descending'
  url = '{}{}&start={}&max_results={}&sortBy={}&sortOrder={}'.format(
    base_url, search_query, start, max_results, sort_by, sort_order)
  response = requests.get(url)
  return response


def parse_arxiv_xml(response):
  # Parse the XML response
  feed = feedparser.parse(response.text)
  for entry in feed.entries:
    print(f"Title: {entry.title}")
    print(f"Authors: {entry.author}")
    print(f"Published: {entry.published}")
    print(f"Summary: {entry.summary[:200]}...")
    print(f"PDF Link: {entry.link}\n")
    print('---------------------------------')
