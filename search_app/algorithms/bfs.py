"""
algorithms/bfs.py
=================
Busca em Amplitude (BFS).
"""


from algorithms.BuscaNP   import buscaNP
from search_result        import SearchResult
from algorithms.conversor import Conversor


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:

    nos, grafo = Conversor.converter_grafo(graph)

    caminho = buscaNP().amplitude_grafo(start, goal, nos, grafo)

    if caminho is None:
        return SearchResult()

    return SearchResult(
        path=caminho,
        cost= Conversor.calcular_custo(caminho, graph),
        depth=len(caminho) - 1
    )