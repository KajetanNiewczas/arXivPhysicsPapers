import magic
import gzip
import tarfile
import os
import shutil


def check_gzip(file_path):
  '''Check if the downloaded file is a gzip archive.'''

  # Get the MIME type of the file
  mime = magic.Magic(mime=True)
  mime_type = mime.from_file(file_path)

  if "gzip" in mime_type:
    print(f"File {file_path} is a gzip archive")
    return True
  else:
    print(f"File {file_path} is an unknown type")
    return None


def extract_gzip(gz_file_path, extracted_dir):
  '''Extract the contents of the gzip archive.'''

  # Get the base name of the gzip file
  file_name = os.path.basename(gz_file_path)
  file_name = file_name.replace('.gz', '').replace('.tar', '')
  file_dir  = os.path.join(extracted_dir, file_name)

  try:
    # Create the directory to extract the contents to
    os.makedirs(file_dir, exist_ok=False)

    with gzip.open(gz_file_path, 'rb') as f_in:
      try:
        # Attempt to extract the tarball
        with tarfile.open(fileobj=f_in, mode='r:') as tar:
          tar.extractall(path=file_dir)
          print(f"Extracted contents of {gz_file_path} to {file_dir}")
        # Extraction complete, remove the archive
        os.remove(gz_file_path)
        return file_dir
      except tarfile.TarError:
        # If the file is not a tarball, extract the single file
        original_name = get_original_filename_from_gzip(gz_file_path)
        if original_name:
          file_path = os.path.join(file_dir, original_name)
        else:
          file_path = os.path.join(file_dir, "source.tex")
        with open(file_path, 'wb') as f_out:
          f_out.write(f_in.read())
          print(f"Extracted contents of {gz_file_path} to {file_dir}")
        # Extraction complete, remove the archive
        os.remove(gz_file_path)
        return file_dir
  except Exception as e:
    # Something went wrong, remove the archive
    os.remove(gz_file_path)
    print(f'Error extracting {gz_file_path}: {e}')
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


def clear_extracted_folder(extracted_path):
  '''Extract the source .tex file from the folder.'''

  # Get the list of .tex files
  files_in_folder = os.listdir(extracted_path)
  tex_files = [f for f in files_in_folder if f.endswith('.tex')]

  # Delete everything else
  for f in files_in_folder:
    if f not in tex_files:
      if os.path.isdir(f):
        shutil.rmdir(os.path.join(extracted_path, f))
      else:
        os.remove(os.path.join(extracted_path, f))

  return True if tex_files else False