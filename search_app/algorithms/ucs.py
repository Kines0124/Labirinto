"""
algorithms/ucs.py
=================
Uniform Cost Search (UCS).
"""

from search_result             import SearchResult
from algorithms.graphConverter import GraphConverter
from algorithms.BuscaP         import WeightedSearch


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
   
   nodes, formatted_graph = GraphConverter.convert_weighted_graph(graph)

   result = WeightedSearch().uniform_cost_graph(start, goal, nodes, formatted_graph)

   if result is None:
      return SearchResult()
   
   path, cost = result
   reverse = path[::-1]       

   return SearchResult(
      path=reverse,
      cost=float(cost),
      depth=len(path) - 1
   )
