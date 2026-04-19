"""
algorithms/heuristica.py
========================
Calcula a heurística admissível para cada nó do grafo em relação
a um objetivo escolhido dinamicamente.

Estratégia atual (grafo estático)
----------------------------------
Roda Dijkstra a partir do OBJETIVO no grafo invertido.
O custo real mínimo de cada nó até o objetivo é uma heurística
perfeitamente admissível (nunca superestima).
"""

import heapq


def calcular_heuristica(goal, graph: dict) -> dict:

    # monta grafo invertido: aresta A->B vira B->A
    grafo_inv = {n: [] for n in graph}
    for origem, vizinhos in graph.items():
        for destino, custo in vizinhos:
            if destino in grafo_inv:
                grafo_inv[destino].append((origem, custo))

    # Dijkstra a partir do objetivo no grafo invertido
    dist = {n: float('inf') for n in graph}
    dist[goal] = 0.0
    heap = [(0.0, goal)]

    while heap:
        custo_atual, no_atual = heapq.heappop(heap)
        if custo_atual > dist[no_atual]:
            continue
        for vizinho, custo_aresta in grafo_inv.get(no_atual, []):
            novo_custo = custo_atual + custo_aresta
            if novo_custo < dist[vizinho]:
                dist[vizinho] = novo_custo
                heapq.heappush(heap, (novo_custo, vizinho))

    return dist

def calcular_heuristica_manhattan(goal: str, graph: dict, coordenadas: list = None) -> dict:
    def parse_coord(s: str):
        s = s.strip("() ")
        x, y = s.split(",")
        return int(x), int(y)

    gx, gy = parse_coord(goal)

    return {
        no: abs(parse_coord(no)[0] - gx) + abs(parse_coord(no)[1] - gy)
        for no in graph
    }