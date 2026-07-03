"""
algorithms/ida_star.py
======================
Iterative Deepening A*.
"""

from   search_result              import SearchResult
from   algorithms.BuscaP          import WeightedSearch
from   algorithms.graphConverter  import GraphConverter
import algorithms.heuristics      as     heuristics


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None,
           heuristic_name: str = 'manhattan') -> SearchResult:
   
   weights = heuristic if heuristic is not None else \
         heuristics.calculate_heuristic_by_name(heuristic_name, goal, graph)

   nodes, formatted_graph = GraphConverter.convert_weighted_graph(graph)
   result  = WeightedSearch().ida_star_graph(start, goal, nodes, formatted_graph, weights)

   if result is None:
      return SearchResult()

   path, cost = result  
   reverse = path[::-1]       

   return SearchResult(
        path=reverse,
        cost=float(cost),
        depth=len(path) - 1
   )
