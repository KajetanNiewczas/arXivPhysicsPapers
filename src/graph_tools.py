class GraphError(Exception):
    """Exception raised if the graph tools fail."""
    pass


def has_cycle(graph):
  '''Find a cycle in a graph.'''
  visited = set()
  in_recursion_stack = set()

  def dfs(node):
    '''Depth-First Search.'''
    if node in in_recursion_stack:
      return True  # Found a cycle
    if node in visited:
      return False # Already processed this node

    visited.add(node)
    in_recursion_stack.add(node)
        
    for neighbor in graph.get(node, []):
      if dfs(neighbor):
        return True
        
    in_recursion_stack.remove(node)
    return False

  for node in graph:
    if node not in visited:
      if dfs(node):
        return True
  return False


def find_main_key(graph):
  '''Find the main node in the graph.'''

  # Collect all child nodes
  all_values = {item for sublist in graph.values() for item in sublist}

  # Check for missing files
  missing_nodes = all_values - set(graph.keys())
  if missing_nodes:
    raise GraphError(f"Missing tex files to include: {', '.join(missing_nodes)}")

  # Ensure there are no cycles first
  if has_cycle(graph):
    raise GraphError("Tex inclusions graph contains a cycle, the structure is ambiguous.")

  # Find the root (main key)
  root_nodes = [key for key in graph if key not in all_values]
  # Return only one, otherwise the structure is ambiguous
  if len(root_nodes) > 1:
    raise GraphError(f"Multiple potential main tex files found: {', '.join(root_nodes)}")
  if root_nodes:
    return root_nodes[0]

  raise GraphError("No main tex found, the structure is ambiguous.")
