import os

from rich import print
import pypandoc

from src.aesthetics import (
  sep_line,
  header,
)
from src.arxiv_api import (
  fetch_paper_metadata,
  download_paper,
  extract_paper,
  copy_source_tex,
)


def main():
  '''Main entry point for the script.'''

  # Make sure we have all the necessary directories
  archive_dir   = 'papers/archives'
  extracted_dir = 'papers/extracted'
  sources_dir   = 'papers/sources'
  os.makedirs(archive_dir,   exist_ok=True)
  os.makedirs(extracted_dir, exist_ok=True)
  os.makedirs(sources_dir,   exist_ok=True)

  # Let's go!
  try:
    # Fetch the metadata of new papers
    # new_papers = fetch_paper_metadata()
    new_papers = [{'arxiv_id': '1902.05618',
                   'title': 'Nuclear Transparency in Monte Carlo Neutrino Event Generators',
                   'source_url': 'https://arxiv.org/src/1902.05618'}]
    for paper in new_papers:
      print(sep_line())
      print(header(f'Processing paper: {paper['arxiv_id']} - {paper['title']}'))

      # # Download the paper source code archive
      # archive_name = download_paper(paper, archive_dir)
      # if not archive_name:
      #   continue

      # # Unpack the archive containing the paper source code
      # paper_name = extract_paper(archive_name, archive_dir, extracted_dir)
      # if not paper_name:
      #   continue

      paper_name = 'test'
      # Copy the source .tex file to the sources directory
      source_name = copy_source_tex(paper_name, extracted_dir, sources_dir)
      if not source_name:
        continue

      # output = pypandoc.convert_text(source_name, 'plain', format='latex')
      # print(output)

    print(sep_line())
    return 0

  except Exception as e:
    print(f'Error: {e}')
    return 1


if __name__ == '__main__':
    main()
