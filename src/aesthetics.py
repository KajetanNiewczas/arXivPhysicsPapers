from rich import print

def sep_line():
  return '[dim]-[/dim]' * 80

def header(string):
  return f'[bold red]{string}[/bold red]'

def link(string):
  return f'[green]\'{string}\'[/green]'
