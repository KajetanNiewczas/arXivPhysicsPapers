import feedparser
import requests
import os


def fetch_paper_metadata(query='all:electron', max_results=1):
  base_url   = 'http://export.arxiv.org/api/query?'
  start      = 0
  sort_by    = 'submittedDate'
  sort_order = 'ascending'     # seems like the best way will be to sort ascanding and then start from next entries
  url = '{}search_query={}&start={}&max_results={}&sortBy={}&sortOrder={}'.format(
    base_url, query, start, max_results, sort_by, sort_order)
  feed = feedparser.parse(url)

  papers = []
  for entry in feed.entries:
    arxiv_id = entry.id.replace('http://arxiv.org/abs/', '') \
                       .replace('https://arxiv.org/abs/', '')
    paper = {
      'title':      entry.title,
      'authors':    [author.name for author in entry.authors],
      'published':  entry.published,
      'summary':    entry.summary,
      'arxiv_id':   arxiv_id,
      'pdf_url':    f'https://arxiv.org/pdf/{arxiv_id}.pdf',
      'source_url': f'https://arxiv.org/src/{arxiv_id}',
    }
    papers.append(paper)

  return papers


def download_paper(paper, save_dir='papers'):
  os.makedirs(save_dir, exist_ok=True)

  arxiv_id    = paper['arxiv_id']
  source_url  = paper['source_url']
  safe_id     = arxiv_id.replace('/', '_')
  source_path = os.path.join(save_dir, f'{safe_id}_source.tar.gz')

  try:
    response = requests.get(source_url, timeout=5)
    if response.ok and len(response.content) > 0:
      with open(source_path, 'wb') as f:
        f.write(response.content)
      print(f'Successfully downloaded {source_path}')
      return source_path
  
  except requests.exceptions.RequestException as e:
    print(f'Error downloading {source_url}: {e}')
    return None

