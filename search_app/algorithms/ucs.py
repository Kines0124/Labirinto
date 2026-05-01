"""
algorithms/ucs.py
=================
Custo Uniforme (Uniform Cost Search — UCS).
"""

from search_result        import SearchResult
from algorithms.conversor import Conversor
from algorithms.BuscaP    import buscaP


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
   
   nos, grafo = Conversor.converter_grafo_ponderado(graph)

   resultado = buscaP().custo_uniforme_grafo(start, goal, nos, grafo)

   if resultado is None:
      return SearchResult()
   
   caminho, custo = resultado
   reverso = caminho[::-1]        # inverte a tupla

   return SearchResult(
      path=reverso,
      cost=float(custo),
      depth=len(caminho) - 1
   )
