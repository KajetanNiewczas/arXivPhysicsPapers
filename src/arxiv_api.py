import os

import requests
import feedparser

from src.tools import (
  check_gzip,
  extract_gzip,
)


def fetch_paper_metadata(query='all:electron', max_results=1):
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


def download_paper(paper, archive_dir='papers/archives'):
  '''Download the source code of a paper from arXiv.'''

  source_url  = paper['source_url']

  try:
    response = requests.get(source_url, timeout=5)
    if response.ok and len(response.content) > 0:
      archive_name = None
      if 'Content-Disposition' in response.headers:
        content_disp = response.headers['Content-Disposition']
        if 'filename=' in content_disp:
          archive_name = content_disp.split('filename=')[-1].strip('"')
          archive_path = os.path.join(archive_dir, archive_name)
          with open(archive_path, 'wb') as f:
            f.write(response.content)
          print(f'Successfully downloaded {archive_path}')
          return archive_name

  except requests.exceptions.RequestException as e:
    print(f'Error downloading {source_url}: {e}')
    return None


def get_source_tex(archive_name, archive_dir='papers/archives',
                                 extracted_dir='papers/extracted'):
  '''Check if the downloaded file is a gzip archive.
     If so, extract the source .tex file from the archive.'''


  if check_gzip(os.path.join(archive_dir, archive_name)):
    paper_name = extract_gzip(archive_name, archive_dir, extracted_dir)
    print(paper_name)
    # if extracted_path:
      # merge tex files into one



      # clear_extracted_folder(extracted_path)
      # if source_tex:
      #   print(f'Successfully extracted {source_tex}')
      #   return source_tex

  return None
