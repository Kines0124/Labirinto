"""
algorithms/dls.py
=================
Depth-Limited Search (DLS).
"""

from search_result        import SearchResult
from algorithms.BuscaNP   import UnweightedSearch
from algorithms.conversor import Conversor


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = 3) -> SearchResult:

    nos, grafo = Conversor.converter_grafo(graph)

    caminho = UnweightedSearch().depth_limited_graph(start, goal, nos, grafo, depth_limit)

    if caminho is None:
        return SearchResult()

    return SearchResult(
        path=caminho,
        cost= Conversor.calcular_custo(caminho, graph),
        depth=len(caminho) - 1
    )
