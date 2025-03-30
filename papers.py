import os

from rich import print

from src.aesthetics import (
  sep_line,
  header,
)
from src.arxiv_api import (
  fetch_paper_metadata,
  download_paper,
  extract_source,
  copy_source_tex,
  extract_plain_text
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
    new_papers = fetch_paper_metadata()
    for paper in new_papers:
      try:
        print(sep_line())
        print(header(f'Processing paper: {paper['arxiv_id']} - {paper['title']}'))

        # Download the paper source code archive
        archive_name = download_paper(paper, archive_dir)
        if not archive_name:
          continue

        # Unpack the archive containing the paper source code
        paper_name = extract_source(archive_name, archive_dir, extracted_dir)
        if not paper_name:
          continue

        # Copy the source .tex file to the sources directory
        source_name = copy_source_tex(paper_name, extracted_dir, sources_dir)
        if not source_name:
          continue

        # Convert the .tex source file into plain text
        plain_text = extract_plain_text(source_name, sources_dir)
        if not plain_text:
          continue

        # Add plain text to the paper's content
        paper['content'] = plain_text
        # with open('test.txt', 'w', encoding='utf-8') as f:
        #   f.write(paper['content'])

      except Exception as e:
        print(f'Error processing paper {paper['arxiv_id']}: {e}')

    print(sep_line())
    return 0

  except Exception as e:
    print(f'Error: {e}')
    return 1


if __name__ == '__main__':
    main()
