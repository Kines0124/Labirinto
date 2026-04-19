"""
algorithms/bidi.py
==================
Busca Bidirecional.

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.bidi import search as bidi_search
   - Substitua:  'Bidirecional': _stub_search  →  bidi_search
"""
from algorithms.BuscaNP import buscaNP
from algorithms.conversor import Conversor
from search_result import SearchResult


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
    
   nos, grafo = Conversor.converter_grafo(graph)

   caminho = buscaNP().bidirecional_grafo(start, goal, nos, grafo)

   if caminho is None:
      return SearchResult
    
   return SearchResult(
      path=caminho,
      cost= Conversor.calcular_custo(caminho, graph),
      nodes_expanded=0,
      depth=len(caminho) - 1
   )