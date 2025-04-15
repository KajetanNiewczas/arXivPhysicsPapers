entry_template = {
  'arxiv_id':     None,
  'safe_id':      None,
  'pdf_url':      None,
  'title':        None,
  'authors':      [],
  'abstract':     None,
  'categories':   [],
  'published':    None,
  'comments':     None,
  'license':      None
}

def new_entry(new_id):
  '''Create new entry based on the template.'''

  arxiv_id = new_id.split("v")[0]

  entry = entry_template.copy()
  entry['arxiv_id'] = arxiv_id
  entry['safe_id']  = arxiv_id.replace('/', '')
  entry['pdf_url']  = f'https://arxiv.org/pdf/{arxiv_id}'

  return entry
