import re
import html

from pylatexenc.latex2text import LatexNodes2Text


def clean_pylatexenc(text):
    """Extract plain text using pylatexenc."""

    # Extract plain text and ensure no html character issues
    plain_text = html.unescape(LatexNodes2Text().latex_to_text(text))

    return plain_text


def preprocess_pylatexenc(tex_content):
    """Additional preprocessing before using pylatexenc"""

    # Remove all hyperlinks
    tex_content = re.sub(r"\\href\{.*?\}\{(.*?)\}", r"\1", tex_content)

    # Remove additional user-defined commands
    tex_content = re.sub(
        r"^\s*\\(input|include|def|newcommand)\b.*\n?",
        "",
        tex_content,
        flags=re.MULTILINE,
    )

    # Remove any abstract environment
    tex_content = remove_abstract_commands(tex_content)
    tex_content = re.sub(
        r"\\begin\{abstract\}.*?\\end\{abstract\}", "", tex_content, flags=re.DOTALL
    )

    return tex_content


def postprocess_pylatexenc(plain_text):
    """Additional postprocessing after using pylatexenc"""

    # Remove the header
    plain_text = remove_header(plain_text)

    # Remove excessive whitespace
    plain_text = remove_whitespace(plain_text)

    return plain_text


def remove_header(plain_text):
    """Remove the whole header with metadata."""

    # Match a header pattern, at least 5 '=' characters
    pattern = re.compile(r"^.*?={5,}\n+", re.MULTILINE | re.DOTALL)

    # Remove the header
    plain_text = re.sub(pattern, "", plain_text, count=1)

    return plain_text


def remove_whitespace(plain_text):
    """Remove excessive whitespace."""

    # Remove and trailing whitespaces
    plain_text = plain_text.strip()

    # Remove excessive empty lines
    plain_text = re.sub(r"\n\s*\n+", "\n\n", plain_text)

    # Convert the non-breaking spaces with regular spaces
    plain_text = plain_text.replace("\xa0", " ")

    return plain_text


def remove_abstract_commands(tex_content):
    result = []
    i = 0
    while i < len(tex_content):
        if tex_content[i : i + 9] == "\\abstract":
            if tex_content[i + 9] != "{":
                result.append(tex_content[i])
                i += 1
                continue

            # We've found \abstract{, now parse until matching closing }
            brace_depth = 0
            j = i + 9
            while j < len(tex_content):
                if tex_content[j] == "{":
                    brace_depth += 1
                elif tex_content[j] == "}":
                    brace_depth -= 1
                    if brace_depth == 0:
                        break
                j += 1
            i = j + 1  # Skip past the closing }
        else:
            result.append(tex_content[i])
            i += 1

    return "".join(result)
