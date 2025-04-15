import os
import gzip
import tarfile
import shutil
import re

from rich import print

from src.aesthetics import (
  link,
)


def get_bucket_year_month(bucket_name):
  '''Get the year and month from the bucket name.'''

  match = re.search(r'src_(\d{2})(\d{2})', bucket_name)

  if match:
    year  = int(match.group(1))
    month = int(match.group(2))

    # Convert to full year
    if year < 50:
      year += 2000
    else:
      year += 1900

    return year, month
  
  else:
    return None, None


def extract_bucket_archive(bucket_name, bucket_dir='amazon_s3/files',
                                        archive_dir='papers/archives'):
  '''Extract the contents of the bucket tarball.'''

  papers = []
  bucket_path = os.path.join(bucket_dir, bucket_name)

  # Extract the contents
  with tarfile.open(bucket_path, 'r') as tar:
    for member in tar.getmembers()[:2]:
      if member.isfile() and member.name.endswith('.gz'):
        # Extract only the gzip files, do not process pdfs
        original_name = os.path.basename(member.name)
        target_path = os.path.join(archive_dir, original_name)

        # Extract the files
        with tar.extractfile(member) as f_in:
          with open(target_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        papers.append(original_name.replace('.gz', ''))

    print(f'Successfully extracted {link(len(papers))} papers from {link(bucket_name)}')

    return papers
