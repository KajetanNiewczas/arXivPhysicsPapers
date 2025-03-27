import feedparser
import requests
import os

from src.tools import (
  check_gzip,
  extract_gzip,
  clear_extracted_folder,
)


def fetch_paper_metadata(query='all:electron', max_results=10):
  '''Fetch metadata for papers from the arXiv API.'''

  base_url   = 'http://export.arxiv.org/api/query?'
  start      = 0
  sort_by    = 'submittedDate'
  # sort_order = 'ascending'
  sort_order = 'descending'
  # seems like the best way will be to sort ascanding
  # and then each time start from next entries
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


def download_paper(paper):
  '''Download the source code of a paper from arXiv.'''

  archive_dir = 'papers/archives'
  os.makedirs(archive_dir, exist_ok=True)

  source_url  = paper['source_url']

  try:
    response = requests.get(source_url, timeout=5)
    if response.ok and len(response.content) > 0:
      filename = None
      if 'Content-Disposition' in response.headers:
        content_disp = response.headers['Content-Disposition']
        if 'filename=' in content_disp:
          filename = content_disp.split('filename=')[-1].strip('"')
          archive_path = os.path.join(archive_dir, filename)
          with open(archive_path, 'wb') as f:
            f.write(response.content)
          print(f'Successfully downloaded {archive_path}')
          return archive_path

  except requests.exceptions.RequestException as e:
    print(f'Error downloading {source_url}: {e}')
    return None


def get_source_tex(archive_path):
  '''Check if the downloaded file is a gzip archive.
     If so, extract the source .tex file from the archive.'''
  
  extracted_dir = 'papers/extracted'
  os.makedirs(extracted_dir, exist_ok=True)

  if check_gzip(archive_path):
    extracted_path = extract_gzip(archive_path, extracted_dir)
    if extracted_path:
      clear_extracted_folder(extracted_path)
      # if source_tex:
      #   print(f'Successfully extracted {source_tex}')
      #   return source_tex

  return None
