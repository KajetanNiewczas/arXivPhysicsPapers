import os
import re

from rich import print

from src.aesthetics import (
  link,
)
from src.graph_tools import (
  find_main_key
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

  # Detect all the inclusions to build the connections graph
  connections  = {}
  for tex_file in tex_files:
    connections[tex_file] = detect_inclusions(tex_contents[tex_file])

  # Find the main .tex file and resolve the inclusions
  main_file    = find_main_key(connections)
  main_content = fix_inclusions(tex_contents, main_file)

  # Create a temporary file to store the merged content
  merged_path = os.path.join(paper_path, 'merged.tex')
  with open(merged_path, 'w', encoding='utf-8') as f:
    f.write(main_content)

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

   # Remove excessive empty lines (multiple \n or lines with only whitespace)
  tex_content = re.sub(r'\n\s*\n+', '\n\n', tex_content)
  if tex_content.endswith('\n\n'):
    tex_content = tex_content[:-1]

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
      # Remove any trailing whitespace before `%`
      while result and result[-1].isspace():
        result.pop()

      # If the last remaining character is '\n', remove it
      if result and result[-1] == '\n':
        result.pop()

      # Skip until the end of the line
      while i < n and tex_content[i] != '\n':
        i += 1
      continue

    # Normal content
    result.append(char)
    i += 1

  # Join the result and remove and trailing empty lines in front
  tex_content = ''.join(result)
  tex_content = tex_content.lstrip("\n")

  return tex_content


def detect_inclusions(tex_content):
  '''Detect the include and input statements in the tex content.
     Return a list of files to which they lead.'''

  # Patterns to detect include and input statements
  include_input_pattern = re.compile(
    r'\\(include|input)\s*'             # Match \include or \input
    r'(?:\[\s*([^\]]*?)\s*\])?\s*'      # Optional [options] (group 2)
    r'\{\s*([^}]*)\s*\}',               # Mandatory {filename} (group 3)
    re.MULTILINE | re.DOTALL
  )

  # Find all matches
  matches = []
  for match in include_input_pattern.finditer(tex_content):
    filename = match.group(3).strip()
    if not filename.endswith('.tex'):
      filename += '.tex'
    matches.append(filename)

  return matches


def fix_inclusions(tex_contents, main_file):
  '''Detect the include and input statements in the main tex file.
     Resolve the commands by pasting the appropriate file.'''

  # Prepare the main content
  main_content = tex_contents.pop(main_file)

  # Patterns to detect include and input statements
  include_input_pattern = re.compile(
    r'\\(include|input)\s*'             # Match \include or \input
    r'(?:\[\s*([^\]]*?)\s*\])?\s*'      # Optional [options] (group 2)
    r'\{\s*([^}]*)\s*\}',               # Mandatory {filename} (group 3)
    re.MULTILINE | re.DOTALL
  )

  # Replace matches
  while True:
    updated     = False
    new_content = []
    last_pos    = 0

    for match in include_input_pattern.finditer(main_content):
      # Get the file to include
      filename = match.group(3).strip()
      if not filename.endswith('.tex'):
        filename += '.tex'

      # Append content before the match
      new_content.append(main_content[last_pos:match.start()])

      # Insert the included file
      new_content.append(tex_contents.pop(filename))

      # Move forward
      last_pos = match.end()
      updated = True

    # Append the remaining content
    new_content.append(main_content[last_pos:])
    main_content = ''.join(new_content)

    # Stop if no more replacements were made
    if not updated:
      break

  return main_content
