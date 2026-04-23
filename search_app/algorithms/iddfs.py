"""
algorithms/iddfs.py
===================
Aprofundamento Iterativo (Iterative Deepening DFS — IDDFS).

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.iddfs import search as iddfs_search
   - Substitua:  'Aprofundamento Iterativo (IDDFS)': _stub_search  →  iddfs_search
"""

from search_result import SearchResult
from algorithms.BuscaNP import buscaNP
from algorithms.conversor import Conversor


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = 100) -> SearchResult:

    nos, grafo = Conversor.converter_grafo(graph)

    # chamada direta ao método original — sem modificações
    caminho = buscaNP().aprof_iterativo_grafo(start, goal, nos, grafo, depth_limit)

    if caminho is None:
        return SearchResult()

    return SearchResult(
        path=caminho,
        cost= Conversor.calcular_custo(caminho, graph),
        nodes_expanded=0,
        depth=len(caminho) - 1
    )
