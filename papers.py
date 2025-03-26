from src.arxiv_api import (
  fetch_paper_metadata,
  download_paper
)


def main():
  try:
    papers = fetch_paper_metadata()
    for p in papers:
      print(p)
      download_paper(p)
    return 0

  except Exception as e:
    print(f'Error: {e}')
    return 1


if __name__ == '__main__':
    main()
