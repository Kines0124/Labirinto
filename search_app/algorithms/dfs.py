"""
algorithms/dfs.py
=================
Busca em Profundidade (Depth-First Search — DFS).

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.dfs import search as dfs_search
   - Substitua:  'Profundidade (DFS)': _stub_search  →  dfs_search
"""

from search_result import SearchResult
from algorithms.BuscaNP import buscaNP
from algorithms.conversor import Conversor


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
    
    nos, grafo = Conversor.converter_grafo(graph)

    # chamada direta ao método original — sem modificações
    caminho = buscaNP().profundidade_grafo(start, goal, nos, grafo)

    if caminho is None:
        return SearchResult()

    return SearchResult(
        path=caminho,
        cost= Conversor.calcular_custo(caminho, graph),
        nodes_expanded=0,
        depth=len(caminho) - 1,
    )