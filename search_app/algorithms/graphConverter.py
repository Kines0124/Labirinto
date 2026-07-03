"""
algorithms/graphConverter.py
===================
Helper for weighted and unweighted graph conversions.
Helper for cost calculation.
"""


class GraphConverter(object):
    """Helper class for conversions and calculations."""

    def convert_graph(graph: dict) -> tuple:
        """Converts the graph for use in unweighted searches."""
        nodes     = sorted(graph.keys())
        adjacency = [[neighbor for neighbor, _cost in graph[n]] for n in nodes]
        return nodes, adjacency

    def calculate_cost(path: list, graph: dict) -> float:
        """Recalculates the actual path cost using the weights from config."""
        total = 0.0
        for i in range(len(path) - 1):
            total += dict(graph[path[i]]).get(path[i + 1], 1)
        return total

    def convert_weighted_graph(graph: dict) -> tuple:
        """Converts the graph for use in weighted searches."""
        nodes     = sorted(graph.keys())
        adjacency = [graph[n] for n in nodes]
        return nodes, adjacency