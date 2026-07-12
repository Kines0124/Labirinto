"""
algorithms/heuristica.py
========================
Calculates the admissible heuristic for each node in the graph with respect to a dynamically chosen goal.
It uses three methods:
- Dijkstra, for greater precision.
- Manhattan, for standard map.
- Euclidean, for multiverse.
"""

import config
import heapq
from   multiverse import MultiverseResult 


def calculate_heuristic_by_name(name: str, goal: str, graph: dict) -> dict:
    """Selects and returns the heuristic by name ('manhattan', 'euclidean' or 'dijkstra')."""
    coordinates = list(graph)
    if name == 'dijkstra':
        return calculate_dijkstra_heuristic(goal, graph)
    elif name == 'euclidiana':
        portal_cost = config.MULTIVERSE.portals[0].cost if config.MULTIVERSE and config.MULTIVERSE.portals else 1.0
        return calculate_euclidean_heuristic(goal, graph, config.MULTIVERSE, portal_cost)
    else:
        return calculate_manhattan_heuristic(goal, graph, coordinates)

def calculate_dijkstra_heuristic(goal, graph: dict) -> dict:
    """Admissible heuristic for enhanced search on the regular map and the multiverse."""
    # builds the reversed graph: edge A->B becomes B->A
    reversed_graph = {n: [] for n in graph}
    for source, neighbors in graph.items():
        for target, cost in neighbors:
            if target in reversed_graph:
                reversed_graph[target].append((source, cost))

    # Dijkstra starting from the goal on the reversed graph
    dist = {n: float('inf') for n in graph}
    dist[goal] = 0.0
    heap = [(0.0, goal)]

    while heap:
        current_cost, current_node = heapq.heappop(heap)
        if current_cost > dist[current_node]:
            continue
        for neighbor, edge_cost in reversed_graph.get(current_node, []):
            new_cost = current_cost + edge_cost
            if new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))

    return dist

def calculate_manhattan_heuristic(goal: str, graph: dict, coordinates: list = None) -> dict:
    """Admissible heuristic for search on a regular graph."""
    def parse_coord(s: str):
        s = s.strip("() ")
        x, y = s.split(",")
        return int(x), int(y)

    gx, gy = parse_coord(goal)

    return {
        node: abs(parse_coord(node)[0] - gx) + abs(parse_coord(node)[1] - gy)
        for node in graph
    }

def calculate_euclidean_heuristic(goal: str, graph: dict,
                                  maps_multiverse: 'MultiverseResult',
                                  portal_cost: float = 1.0) -> dict:
    """Admissible heuristic for search on the multiverse supergraph."""

    def parse_node(node: str) -> tuple[int, int, int]:
        if ':' in node:
            map_part, coord_part = node.split(':', 1)
            map_id = int(map_part.lstrip('M'))
        else:
            map_id     = 0
            coord_part = node

        coord_part = coord_part.strip('()')
        r, c       = coord_part.split(',')
        return map_id, int(r), int(c)

    goal_map, goal_r, goal_c = parse_node(goal)

    heuristic = {}
    for node in graph:
        node_map, node_r, node_c = parse_node(node)

        # Euclidean distance to the goal position (within the 2D space)
        spatial_distance = ((node_r - goal_r) ** 2 + (node_c - goal_c) ** 2) ** 0.5

        # Penalty proportional to the number of maps still to cross
        remaining_maps = abs(node_map - goal_map)
        penalty        = remaining_maps * portal_cost

        heuristic[node] = spatial_distance + penalty

    return heuristic