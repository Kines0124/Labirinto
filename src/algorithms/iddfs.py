"""
algorithms/iddfs.py
===================
Iterative Deepening DFS (IDDFS).
"""


from search_result                import SearchResult
from algorithms.unweighted_search import UnweightedSearch
from algorithms.graph_converter   import GraphConverter


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = 100) -> SearchResult:

    nodes, formatted_graph = GraphConverter.convert_graph(graph)

    path = UnweightedSearch().iterative_deepening_graph(start, goal, nodes, formatted_graph, depth_limit)

    if path is None:
        return SearchResult()

    return SearchResult(
        path=path,
        cost= GraphConverter.calculate_cost(path, graph),
        depth=len(path) - 1
    )
