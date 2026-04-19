"""
algorithms/astar.py
===================
A* (A-estrela).

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.astar import search as astar_search
   - Substitua:  'A* (A-estrela)': _stub_search  →  astar_search
"""

from search_result import SearchResult
from algorithms.BuscaP import buscaP
from algorithms.conversor import Conversor
import algorithms.heuristica as heuristica


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None,
           heuristic_name: str = 'manhattan') -> SearchResult:

   pesos = heuristica.calcular_heuristica_por_nome(heuristic_name, goal, graph)

   nos, grafo = Conversor.converter_grafo_ponderado(graph)
   resultado = buscaP().a_estrela_grafo(start, goal, nos, grafo, pesos)

   if resultado is None:
      return SearchResult()

   caminho, custo = resultado  
   reverso = caminho[::-1]        # inverte a tupla

   return SearchResult(
      path=reverso,
      cost=float(custo),
      nodes_expanded=0,
      depth=len(caminho) - 1
   )