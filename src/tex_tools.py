import os
import re

from rich import print

from src.aesthetics import (
  link,
)


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

  # Read the content of all .tex files
  tex_contents = {}
  for tex_file in tex_files:
    with open(os.path.join(paper_path, tex_file), 'r', encoding='utf-8') as f:
      tex_contents[tex_file] = preprocess_tex_content(f.read())

  print(tex_contents['conclusions.tex'])

  # Create a temporary file to store the merged content
  merged_path = os.path.join(paper_path, 'merged.tex')
  with open(merged_path, 'w'): pass

  return merged_path


def preprocess_tex_content(tex_content):
  '''Preprocess the tex file.'''

  # Normalize line endings and excessive whitespaces
  tex_content = normalize_tex(tex_content)

  # Remove comments and excessive empty lines
  tex_content = remove_comments_tex(tex_content)

  return tex_content


def normalize_tex(tex_content):
  '''Preprocessing: normalize line endings and remove excessive whitespace.'''

  # Normalize line endings: Convert \r\n to \n
  tex_content = tex_content.replace('\r\n', '\n')

  # Remove excessive whitespace
  lines = tex_content.split('\n')
  cleaned_lines = []
  for line in lines:
    stripped_line = line.strip()
    cleaned_lines.append(stripped_line)
  tex_content = '\n'.join(cleaned_lines)

  return tex_content


def remove_comments_tex(tex_content):
  '''Preprocessing: remove all comments.'''

  # Where % should be treated literally
  VERBATIM = ['verbatim', 'lstlisting', 'minted']

  # Patterns to match
  begin_env_pattern   = re.compile(r'\\begin\{(\w+)\}')
  end_env_pattern     = re.compile(r'\\end\{(\w+)\}')
  inline_verb_pattern = re.compile(r'(\\(verb|lstinline)\S)(.*?)(?=\1)')
  comment_pattern     = re.compile(r'(?<!\\)%')

  # Initialize variables
  i = 0
  n = len(tex_content)
  result    = []
  env_stack = []  # to keep track of nested environments

  # Iterate through the content character by character
  while i < n:
    char = tex_content[i]

    # Check for the beginning of an environment
    begin_match = begin_env_pattern.match(tex_content, i)
    if begin_match:
      env_name = begin_match.group(1)
      if env_name in VERBATIM:
        env_stack.append(env_name)  # Enter verbatim-like environment
      result.append(tex_content[i:i + begin_match.end() - begin_match.start()])
      i += begin_match.end() - begin_match.start()
      continue

    # Check for the end of an environment
    end_match = end_env_pattern.match(tex_content, i)
    if end_match:
      env_name = end_match.group(1)
      if env_name in VERBATIM and env_stack:
        env_stack.pop()             # Exit verbatim-like environment
      result.append(tex_content[i:i + end_match.end() - end_match.start()])
      i += end_match.end() - end_match.start()
      continue

    # Check for inline verbatim
    verb_match = inline_verb_pattern.match(tex_content, i)
    if verb_match:
      # Extract verbatim content
      prefix    = verb_match.group(1)
      content   = verb_match.group(3)
      delim     = prefix[-1]
      result.append(f"{prefix}{content}{delim}")
      i += len(prefix) + len(content) + len(delim)
      continue

    # Check for comments
    comment_pos = comment_pattern.match(tex_content, i)
    if comment_pos:
      # Skip until the end of the line
      while i < n and tex_content[i] != '\n':
        i += 1
      continue

    # Normal content
    result.append(char)
    i += 1

  # Join the result, but remove the first empty line
  if result and result[0] == '\n':
    result = result[1:]
  tex_content = ''.join(result)

  # Remove excessive empty lines (multiple \n or lines with only whitespace)
  tex_content = re.sub(r'\n\s*\n+', '\n\n', tex_content)
  if tex_content.endswith('\n\n'):
    tex_content = tex_content[:-1]

  return tex_content
