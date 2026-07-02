"""
algorithms/bfs.py
=================
Breadth-First Search (BFS).
"""


from algorithms.BuscaNP   import UnweightedSearch
from search_result        import SearchResult
from algorithms.conversor import Conversor


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:

    nos, grafo = Conversor.converter_grafo(graph)

    caminho = UnweightedSearch().breadth_first_graph(start, goal, nos, grafo)

    if caminho is None:
        return SearchResult()

    return SearchResult(
        path=caminho,
        cost= Conversor.calcular_custo(caminho, graph),
        depth=len(caminho) - 1
    )