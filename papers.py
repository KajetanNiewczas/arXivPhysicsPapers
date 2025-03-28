import os

from rich import print

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
    # new_papers = fetch_paper_metadata()
    new_papers = [{'arxiv_id': '1902.05618',
                   'title': 'Nuclear Transparency in Monte Carlo Neutrino Event Generators',
                   'source_url': 'https://arxiv.org/src/1902.05618'}]
    for paper in new_papers:
      print(f'[dim]-[/dim]' * 80)
      print(f'[bold red]Processing paper: {paper['arxiv_id']} - {paper['title']}[/bold red]')

      archive_name = download_paper(paper, archive_dir)
      if not archive_name:
        continue

      paper_name = extract_paper(archive_name, archive_dir, extracted_dir)
      if not paper_name:
        continue

      source_name = copy_source_tex(paper_name, extracted_dir, sources_dir)
      if not source_name:
        continue

    print(f'[dim]-[/dim]' * 80)
    return 0

  except Exception as e:
    print(f'Error: {e}')
    return 1


if __name__ == '__main__':
    main()
