"""
algorithms/_stub.py
===================
Implementação temporária usada enquanto os algoritmos reais não existem.
Retorna um caminho aleatório apenas para demonstrar a interface.

REMOVA este arquivo (e suas referências em __init__.py) após implementar
todos os algoritmos reais.
"""

import random
from search_result import SearchResult


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = 3) -> SearchResult:
    """Stub: caminha aleatoriamente pelo grafo até atingir o objetivo ou esgotar tentativas."""
    path = [start]
    current = start
    visited = {start}

    for _ in range(10):
        neighbors = [n for n, _ in graph.get(current, []) if n not in visited]
        if not neighbors:
            break
        current = random.choice(neighbors)
        path.append(current)
        visited.add(current)
        if current == goal:
            break

    cost = sum(
        next((c for n, c in graph[path[i]] if n == path[i + 1]), 1)
        for i in range(len(path) - 1)
    )

    return SearchResult(
        path=path,
        cost=cost,
        nodes_expanded=random.randint(5, 20),
        depth=len(path) - 1,
    )
