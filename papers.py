import os

from src.arxiv_api import (
  fetch_paper_metadata,
  download_paper,
  get_source_tex,
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
    new_papers = fetch_paper_metadata()
    for paper in new_papers:
      print(paper)
      archive_name = download_paper(paper, archive_dir)
      get_source_tex(archive_name)
    return 0

  except Exception as e:
    print(f'Error: {e}')
    return 1


if __name__ == '__main__':
    main()
