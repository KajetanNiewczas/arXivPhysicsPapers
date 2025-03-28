from rich import print

def sep_line():
  '''Return a separator line.'''
  return '[dim]-[/dim]' * 80

def header(string):
  '''Return a header string.'''
  return f'[bold red]{string}[/bold red]'

def link(string):
  '''Return a string that represents a link.'''
  return f'[green]\'{string}\'[/green]'
