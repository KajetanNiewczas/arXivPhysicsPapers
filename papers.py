import os
import time
import json
import re
import argparse

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
    fetch_paper_oaipmh,
    fetch_full_month_oaipmh,
    match_paper_metadata_xml,
    match_paper_metadata_json,
    download_paper,
    extract_source,
    copy_source_tex,
    extract_plain_text,
)
from src.bucket_tools import (
    get_bucket_year_month,
    extract_bucket_archive,
)


def main():
    """Main entry point for the script."""

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Process arXiv bucket tarball and build database."
    )
    parser.add_argument("tarball", help="Name of the .tar file to process")
    args = parser.parse_args()

    # Make sure we have all the necessary directories
    database_dir = "database"
    archive_dir = "papers/archives"
    extracted_dir = "papers/extracted"
    sources_dir = "papers/sources"
    os.makedirs(database_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(extracted_dir, exist_ok=True)
    os.makedirs(sources_dir, exist_ok=True)

    # Metadata database file
    metadata_file = "metadata/arxiv-metadata-oai-snapshot.json"

    # Set the bucket name and database file name
    bucket_name = args.tarball
    database_name = re.sub(r"^arXiv_src_(.*)\.tar$", r"\1.jsonl", bucket_name)
    database_file = os.path.join(database_dir, database_name)
    # Guard against overwriting
    if os.path.exists(database_file):
        confirm = (
            input(f"File '{database_file}' already exists. Overwrite? [y/N]: ")
            .strip()
            .lower()
        )
        if confirm != "y":
            print("Aborting to prevent overwrite!")
            exit(0)

    # Let's go!
    entries = []
    try:
        # Unpack the archive with papers
        papers = extract_bucket_archive(
            bucket_name, bucket_dir="amazon_s3/files", archive_dir=archive_dir
        )
        if not papers:
            raise RuntimeError("No papers found in the bucket")

        # Get the year and month from the bucket name
        year, month = get_bucket_year_month(bucket_name)
        if not year or not month:
            raise RuntimeError("Failed to extract year and month from the bucket name")

        # If we have the OAI-PMH metadata database file
        if os.path.exists(metadata_file):
            with open(metadata_file, "r", encoding="utf-8") as f:
                # Load the records as a generator
                records_json = (json.loads(line) for line in f)
                # Match the metadata with the papers
                entries += match_paper_metadata_json(papers, records_json)
        else:
            # If the year and month is later than the start of OAI-PMH
            if year > 2007 or (year == 2007 and month > 4):
                # Fetch the set of metadata for the given month
                records_xml = fetch_full_month_oaipmh(year, month)
                # Match the metadata with the papers
                entries += match_paper_metadata_xml(papers, records_xml)

        # Manually deal with the rest of the papers one by one
        while papers:
            # Get the next paper
            entry = new_entry(papers.pop(0))

            try:
                # Respect the arXiv guidelines and sleep for 3 seconds before the next request
                time.sleep(3)
                # Fetch the metadata using OAI-PMH
                if fetch_paper_oaipmh(entry):
                    entries.append(entry)
            except Exception as e:
                print(f"Failed to fetch metadata for {link(entry['arxiv_id'])}: {e}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    print(f"Total papers to process: {len(entries)}")

    try:
        with open(database_file, "a", encoding="utf-8") as db_file:

            # Process the entries
            for entry in entries:
                try:
                    print(sep_line())
                    print(header(f"Processing paper: {entry['arxiv_id']}"))

                    # Download the paper source code archive
                    archive_name = entry["safe_id"] + ".gz"
                    if not archive_name:
                        raise RuntimeError(
                            f"Download failed for {link(entry['arxiv_id'])}"
                        )

                    # Unpack the archive containing the paper source code
                    paper_name = extract_source(
                        archive_name, archive_dir, extracted_dir
                    )
                    if not paper_name:
                        raise RuntimeError(
                            f"Unpacking failed for {link(entry['arxiv_id'])}"
                        )

                    # Copy the source .tex file to the sources directory
                    source_name = copy_source_tex(
                        paper_name, extracted_dir, sources_dir
                    )
                    if not source_name:
                        raise RuntimeError(
                            f"Copying a source .tex file failed for {link(entry['arxiv_id'])}"
                        )

                    # Convert the .tex source file into plain text
                    plain_text = extract_plain_text(source_name, sources_dir)
                    if not plain_text:
                        continue

                    # Add plain text to the paper's content
                    entry["content"] = plain_text

                    # Clean the unnecessary fields from the entry
                    del entry["safe_id"]

                    # Think about licenses, it seems that
                    # ['CC BY 4.0', 'CC BY-SA 4.0', 'CC BY-NC-SA 4.0', 'CC BY-NC-ND 4.0', 'CC Zero']
                    # allow for redistribution of the contents, i.e. putting it in a public database

                    # Save the entry to the database file
                    db_file.write(json.dumps(entry) + "\n")

                except Exception as e:
                    print(f"Error processing paper {entry['arxiv_id']}: {e}")

            print(sep_line())

        print(header(f"Processing complete. Entries saved to {link(database_file)}"))

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    main()
