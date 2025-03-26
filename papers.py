from src.arxiv_api import (
  access_arxiv_api,
  parse_arxiv_xml
)


def main():
  try:
    response = access_arxiv_api()
    parse_arxiv_xml(response)
    return 0

  except Exception as e:
    print(f"Error: {e}")
    return 1


if __name__ == "__main__":
    main()
