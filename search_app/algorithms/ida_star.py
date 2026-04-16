"""
algorithms/ida_star.py
======================
AIA* — A* Iterativo (Iterative Deepening A*).

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.ida_star import search as ida_star_search
   - Substitua:  'AIA* (A* Iterativo)': _stub_search  →  ida_star_search
"""

from search_result import SearchResult
from algorithms.BuscaP import buscaP
from algorithms.conversor import Conversor
from algorithms import Heuristica


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
   
   nos, grafo = Conversor.converter_grafo_ponderado(graph)

   buscador = buscaP()

   buscador._heuristica = Heuristica.calcular_heuristica(goal, graph)


   resultado = buscaP().aia_estrela_grafo(start, goal, nos, grafo)

   if resultado is None:
      return SearchResult()

   caminho, custo = resultado  
   reverso = caminho[::-1]        # inverte a tupla

   return SearchResult(
        path=reverso,
        cost=Conversor.calcular_custo(caminho, graph),
        nodes_expanded=0,
        depth=len(caminho) - 1,
   )
