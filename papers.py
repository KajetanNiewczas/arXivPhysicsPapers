import os

from rich import print

from src.aesthetics import (
  sep_line,
  header,
  link,
)
from src.entries import (
  new_entry,
)
from src.arxiv_api import (
  fetch_paper_metadata,
  get_paper_oaipmh,
  download_paper,
  extract_source,
  copy_source_tex,
  extract_plain_text
)
from src.bucket_tools import (
  extract_bucket_archive,
)


def main():
  '''Main entry point for the script.'''

  # We are writing to papers.jsonl
  database_file = 'database/papers.jsonl'
  if not os.path.exists(database_file):
    open(database_file, 'w').close()

  # Make sure we have all the necessary directories
  archive_dir   = 'papers/archives'
  extracted_dir = 'papers/extracted'
  sources_dir   = 'papers/sources'
  os.makedirs(archive_dir,   exist_ok=True)
  os.makedirs(extracted_dir, exist_ok=True)
  os.makedirs(sources_dir,   exist_ok=True)

  # Let's go!
  papers = []
  try:
    # Unpack the archive with papers
    papers = [new_entry(x) for x in extract_bucket_archive('arXiv_src_1001_001.tar',
                                                           bucket_dir='amazon_s3/files',
                                                           archive_dir=archive_dir)]
    if not papers:
      raise RuntimeError('No papers found in the archive')

    # Fetch the list of papers
    # papers = [new_entry(x) for x in fetch_paper_metadata()]
    # papers = [new_entry('1902.05618')]
    # papers = [new_entry('1702.06402')]
    # for paper in papers:
    #   try:
    #     print(sep_line())
    #     print(header(f'Processing paper: {paper['arxiv_id']}'))

    #     # Get metadata of the paper
    #     if not get_paper_oaipmh(paper):
    #       raise RuntimeError(f'Failed to fetch metadata of {link(paper['arxiv_id'])}')

    #     # Download the paper source code archive
    #     archive_name = download_paper(paper, archive_dir)
    #     if not archive_name:
    #       raise RuntimeError(f'Download failed for {link(paper['arxiv_id'])}')

    #     # Unpack the archive containing the paper source code
    #     paper_name = extract_source(archive_name, archive_dir, extracted_dir)
    #     if not paper_name:
    #       raise RuntimeError(f'Unpacking failed for {link(paper['arxiv_id'])}')

    #     # Copy the source .tex file to the sources directory
    #     source_name = copy_source_tex(paper_name, extracted_dir, sources_dir)
    #     if not source_name:
    #       raise RuntimeError(f'Copying a source .tex file failed for {link(paper['arxiv_id'])}')

    #     # Convert the .tex source file into plain text
    #     plain_text = extract_plain_text(source_name, sources_dir)
    #     if not plain_text:
    #       continue

    #     # Add plain text to the paper's content
    #     paper['content'] = plain_text
    #     with open('test.txt', 'w', encoding='utf-8') as f:
    #       f.write(paper['content'])

        # Think about licenses, it seems that
        # ['CC BY 4.0', 'CC BY-SA 4.0', 'CC BY-NC-SA 4.0', 'CC BY-NC-ND 4.0', 'CC Zero']
        # allow for redistribution of the contents, i.e. putting it in a public database

      # except Exception as e:
        # print(f'Error processing paper {paper['arxiv_id']}: {e}')

    print(sep_line())
    return 0

  except Exception as e:
    print(f'Error: {e}')
    return 1


if __name__ == '__main__':
    main()
