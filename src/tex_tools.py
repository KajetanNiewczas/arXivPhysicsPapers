import os


def find_tex_files(root_dir):
  '''Find all .tex files in the root directory.'''

  tex_files = []
  for root, _, files in os.walk(root_dir):
    for file in files:
      if file.endswith('.tex'):
        relative_path = os.path.relpath(os.path.join(root, file), root_dir)
        tex_files.append(relative_path)

  return tex_files


def merge_tex_files(tex_files, paper_path):
  '''Merge multiple .tex files into a single file.'''

  # Create a temporary file to store the merged content
  merged_path = os.path.join(paper_path, 'merged.tex')

  # Read the content of all .tex files
  tex_contents = {}
  for tex_file in tex_files:
    with open(os.path.join(paper_path, tex_file), 'r') as f:
      tex_contents[tex_file] = f.read()



  print("nothing implemented yet")
  return merged_path
