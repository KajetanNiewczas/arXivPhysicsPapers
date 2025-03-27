from src.arxiv_api import (
  fetch_paper_metadata,
  download_paper,
  get_source_tex,
)


def main():
  try:
    papers = fetch_paper_metadata()
    for p in papers:
      print(p)
      archive = download_paper(p)
      get_source_tex(archive)
    return 0

  except Exception as e:
    print(f'Error: {e}')
    return 1


if __name__ == '__main__':
    main()
