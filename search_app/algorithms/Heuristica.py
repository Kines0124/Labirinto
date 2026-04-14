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
    """
    Retorna {nó: custo_estimado_até_goal} para todos os nós do grafo.

    Usa Dijkstra no grafo invertido a partir do objetivo, garantindo
    que h(n) <= custo_real(n, goal) para todo n (admissibilidade).

    Parâmetros
    ----------
    goal  : estado objetivo escolhido pelo usuário
    graph : {estado: [(vizinho, custo), ...]}

    Retorna
    -------
    dict — h(goal) == 0, nós inalcançáveis retornam inf
    """
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