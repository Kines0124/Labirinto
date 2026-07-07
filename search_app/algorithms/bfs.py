"""
algorithms/bfs.py
=================
Breadth-First Search (BFS).
"""


from algorithms.BuscaNP        import UnweightedSearch
from search_result             import SearchResult
from algorithms.graphConverter import GraphConverter


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:

    nodes, formatted_graph = GraphConverter.convert_graph(graph)

    path = UnweightedSearch().breadth_first_graph(start, goal, nodes, formatted_graph)

    if path is None:
        return SearchResult()

    return SearchResult(
        path=path,
        cost= GraphConverter.calculate_cost(path, graph),
        depth=len(path) - 1
    )