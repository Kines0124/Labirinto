"""
algorithms/ida_star.py
======================
Iterative Deepening A*.
"""

from   search_result         import SearchResult
from   algorithms.BuscaP     import WeightedSearch
from   algorithms.conversor  import Conversor
import algorithms.heuristica as     heuristica


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None,
           heuristic_name: str = 'manhattan') -> SearchResult:
   
   pesos = heuristic if heuristic is not None else \
         heuristica.calcular_heuristica_por_nome(heuristic_name, goal, graph)

   nos, grafo = Conversor.converter_grafo_ponderado(graph)
   resultado  = WeightedSearch().ida_star_graph(start, goal, nos, grafo, pesos)

   if resultado is None:
      return SearchResult()

   caminho, custo = resultado  
   reverso = caminho[::-1]        # inverte a tupla

   return SearchResult(
        path=reverso,
        cost=float(custo),
        depth=len(caminho) - 1
   )
