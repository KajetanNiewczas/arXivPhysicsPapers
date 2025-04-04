import os
import shutil
import html
import xml.etree.ElementTree as ET

from rich import print
import requests
import feedparser

from src.aesthetics import (
  link,
)
from src.gzip_tools import (
  check_gzip,
  extract_gzip,
)
from src.tex_tools import (
  find_tex_files,
  merge_tex_files,
)
from src.pylatexenc_tools import (
  clean_pylatexenc,
  preprocess_pylatexenc,
  postprocess_pylatexenc,
)


# Warning: this will most likely be depricated
def fetch_paper_metadata(query='all:electron', max_results=1):
  '''Fetch metadata for papers from the arXiv API.'''

  base_url   = 'http://export.arxiv.org/api/query?'
  start      = 0
  sort_by    = 'submittedDate'
  sort_order = 'descending'
  # sort_order = 'descending'
  # seems like the best way will be to sort ascanding
  # and then each time start from next entries
  url = '{}search_query={}&start={}&max_results={}&sortBy={}&sortOrder={}'.format(
    base_url, query, start, max_results, sort_by, sort_order)
  feed = feedparser.parse(url)

  papers = []
  for entry in feed.entries:
    arxiv_id = entry.id.replace('http://arxiv.org/abs/', '') \
                       .replace('https://arxiv.org/abs/', '')
    papers.append(arxiv_id)
  #   paper = {
  #     'title':          entry.title,
  #     'authors':        [author.name for author in entry.authors],
  #     'published':      entry.published,
  #     'summary':        entry.summary,
  #     'arxiv_id':       arxiv_id,
  #     'pdf_url':        f'https://arxiv.org/pdf/{arxiv_id}.pdf',
  #     'source_url':     f'https://arxiv.org/src/{arxiv_id}',
  #     'primary_cat':    entry.arxiv_primary_category['term'],
  #     'secondary_cats': [cat.term for cat in entry.tags
  #                        if cat.term != entry.arxiv_primary_category['term']]
  #   }
  #   papers.append(paper)

  return papers


def get_paper_oaipmh(paper):
  '''Get metadata for papers using the arXiv OAI-PMH.'''

  # arXiv id of the paper
  arxiv_id = paper['arxiv_id']

  # Access the API
  base_url = 'http://export.arxiv.org/oai2?'
  verb     = 'GetRecord'
  prefix   = 'arXiv'
  url = '{}verb={}&metadataPrefix={}&identifier=oai:arXiv.org:{}'.format(
    base_url, verb, prefix, arxiv_id)
  response = requests.get(url)

  # Check if the query was resolved correctly
  if response.status_code != 200:
    raise RuntimeError(f'Failed to fetch metadata of {link(arxiv_id)} - HTTP {response.status_code}')

  # Parse the response
  NAMESPACE = {'arxiv': 'http://arxiv.org/OAI/arXiv/'}
  root = ET.fromstring(response.text)
  metadata = root.find('.//arxiv:arXiv', NAMESPACE)
  if metadata is None:
    raise ValueError(f'No metadata found for {link(arxiv_id)}')

  # Extract title
  if metadata.find('arxiv:title', NAMESPACE) is not None:
    paper['title'] = " ".join(clean_pylatexenc(metadata.find('arxiv:title', NAMESPACE).text).split())
  else:
    raise ValueError(f'Missing title for {link(arxiv_id)}')

  # Extract authors
  if metadata.find('arxiv:authors', NAMESPACE) is not None:
    paper['authors'] = [
      " ".join(filter(None, [
        html.unescape(author.find('arxiv:forenames', NAMESPACE).text) if author.find('arxiv:forenames', NAMESPACE) is not None else None,
        html.unescape(author.find('arxiv:keyname', NAMESPACE).text)
    ]))
    for author in metadata.findall('arxiv:authors/arxiv:author', NAMESPACE)
    ]
  else:
    raise ValueError(f'Missing authors for {link(arxiv_id)}')

  # Extract abstract
  if metadata.find('arxiv:abstract', NAMESPACE) is not None:
    paper['abstract'] = " ".join(clean_pylatexenc(metadata.find('arxiv:abstract', NAMESPACE).text).split())
  else:
    raise ValueError(f'Missing abstract for {link(arxiv_id)}')
  
  # Extract categories
  if metadata.find('arxiv:categories', NAMESPACE) is not None:
    paper['categories'] = [x for x in metadata.find('arxiv:categories', NAMESPACE).text.split()]
  else:
    raise ValueError(f'Missing categories for {link(arxiv_id)}')

  # Extract non-obligatory fields
  paper['published'] = metadata.find('arxiv:journal-ref', NAMESPACE).text \
    if metadata.find('arxiv:journal-ref', NAMESPACE) is not None else None
  paper['comments'] = metadata.find('arxiv:comments', NAMESPACE).text \
    if metadata.find('arxiv:comments', NAMESPACE) is not None else None
  paper['license'] = metadata.find('arxiv:license', NAMESPACE).text \
    if metadata.find('arxiv:license', NAMESPACE) is not None else None

  return True


def download_paper(paper, archive_dir='papers/archives'):
  '''Download the source code of a paper from arXiv.'''

  source_url  = paper['pdf_url'].replace('pdf', 'src')

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
        print(f'Successfully downloaded {link(archive_path)}')
        return archive_name

  return None


def extract_source(archive_name, archive_dir='papers/archives',
                                extracted_dir='papers/extracted'):
  '''Extract the contents of the gzip archive.'''

  # Check if we have a gzip archive and extract it
  if check_gzip(os.path.join(archive_dir, archive_name)):
    paper_name = extract_gzip(archive_name, archive_dir, extracted_dir)

  return paper_name


def copy_source_tex(paper_name, extracted_dir='papers/extracted',
                                sources_dir='papers/sources'):
  '''Copy the source .tex file to the sources directory.'''

  # Get the list of .tex files
  paper_path = os.path.join(extracted_dir, paper_name)
  tex_files  = find_tex_files(paper_path)
  if not tex_files:
    print(f"Warning: there no tex files to process for {link(paper_name)}")
    return None

  # Check if the source file already exists
  source_name = paper_name + '.tex'
  source_path = os.path.join(sources_dir, source_name)
  if os.path.exists(source_path):
    print(f'Warning: {link(source_name)} already exists and will be overwritten')

  # Preprocess .tex files, merge then if needed and copy the result
  merged_path = merge_tex_files(tex_files, paper_path)
  shutil.copy(merged_path, source_path)

  # Remove the extracted folder
  shutil.rmtree(paper_path)
  print(f'Successfully copied {link(source_name)} and removed {link(paper_path)}')

  return source_name


def extract_plain_text(source_name, sources_dir):
  '''Extract plain text from a .tex source file.'''

  # Load the .tex source file
  tex_content = None
  source_path = os.path.join(sources_dir, source_name)
  with open(source_path, 'r') as f:
    tex_content = f.read()

  # Convert to plain text using pylatexenc
  plain_text = postprocess_pylatexenc(
                 clean_pylatexenc(
                   preprocess_pylatexenc(tex_content)
                 )
               )

  # Remove the source file
  os.remove(source_path)
  print(f'Extracted plain text from {link(source_path)}')

  return plain_text

