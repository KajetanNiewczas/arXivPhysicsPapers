import os
import gzip
import tarfile
import shutil

from rich import print
import magic

from src.aesthetics import (
  link,
)


def check_gzip(file_path):
  '''Check if the downloaded file is a gzip archive.'''

  # Get the MIME type of the file
  mime = magic.Magic(mime=True)
  mime_type = mime.from_file(file_path)

  if "gzip" in mime_type:
    print(f"File {link(file_path)} is a gzip archive")
    return True
  else:
    print(f"File {link(file_path)} is an unknown type")
    return None


def extract_gzip(archive_name, archive_dir, extracted_dir):
  '''Extract the contents of the gzip archive.'''

  # Get the base name of the gzip file
  archive_path = os.path.join(archive_dir, archive_name)
  paper_name   = archive_name.replace('.gz', '').replace('.tar', '')
  paper_dir    = os.path.join(extracted_dir, paper_name)

  try:
    # Create the directory to extract the contents to
    os.makedirs(paper_dir, exist_ok=False)

    with gzip.open(archive_path, 'rb') as f_in:
      try:
        # Attempt to extract the tarball
        with tarfile.open(fileobj=f_in, mode='r:') as tar:
          tar.extractall(path=paper_dir)
          print(f"Extracted contents of {link(archive_path)} to {link(paper_dir)}")
        # Extraction complete, remove the archive
        os.remove(archive_path)
        return paper_name
      except tarfile.TarError:
        # If the file is not a tarball, extract the single file
        original_name = get_original_filename_from_gzip(archive_path)
        if original_name:
          file_path = os.path.join(paper_dir, original_name)
        else:
          file_path = os.path.join(paper_dir, "source.tex")
        with gzip.open(archive_path, 'rb') as f_in:
          with open(file_path, 'wb') as f_out:
            f_out.write(f_in.read())
            print(f"Extracted contents of {link(archive_path)} to {link(paper_dir)}")
        # Extraction complete, remove the archive
        os.remove(archive_path)
        return paper_name
  except Exception as e:
    # Something went wrong, remove the empty folder
    shutil.rmtree(paper_dir)
    print(f'Error extracting {link(archive_path)}: {e}')
    return None


def get_original_filename_from_gzip(gz_file_path):
  '''Extract the original filename from the gzip file header.'''

  with open(gz_file_path, 'rb') as f:
    # Skip the first 10 bytes of the gzip header
    f.seek(10)
    # Read the filename length byte (null-terminated)
    filename = bytearray()
    while True:
      byte = f.read(1)
      if byte == b'\0':  # Null byte indicates end of filename
        break
      filename.extend(byte)

  return filename.decode('utf-8') if filename else None
