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

import config
import heapq
from   multiverse import MultiverseResult 


def calcular_heuristica_dijkstra(goal, graph: dict) -> dict:

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


def calcular_heuristica_por_nome(nome, goal, graph):
    # Se o nó usa prefixo de mapa, força Dijkstra
    if goal.startswith("M") and ":" in goal:
        return calcular_heuristica_dijkstra(goal, graph)
    # Comportamento original para mapa único
    coordenadas = list(graph)
    if nome == 'dijkstra':
        return calcular_heuristica_dijkstra(goal, graph)
    return calcular_heuristica_manhattan(goal, graph, coordenadas)

def calcular_heuristica_por_nome(nome: str, goal: str, graph: dict) -> dict:
    """Seleciona e retorna a heurística pelo nome ('manhattan' ou 'dijkstra')."""
    coordenadas = list(graph)
    if nome == 'dijkstra':
        return calcular_heuristica_dijkstra(goal, graph)
    elif nome == 'euclidiana':
        portal_cost = config.MULTIVERSE.portals[0].cost if config.MULTIVERSE and config.MULTIVERSE.portals else 1.0
        return calcular_heuristica_euclidiana(goal, graph, config.MULTIVERSE, portal_cost)
    else:
        return calcular_heuristica_manhattan(goal, graph, coordenadas)


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

def calcular_heuristica_euclidiana(goal: str, graph: dict,
                                   maps_multiverse: 'MultiverseResult',
                                   portal_cost: float = 1.0) -> dict:
    """
    Heurística admissível para busca no supergráfico do multiverso.

    Para cada nó n, estima o custo restante até goal como:
        h(n) = distância_euclidiana(n, goal_local) + penalidade_de_mapas

    onde:
        distância_euclidiana  = sqrt((dr)² + (dc)²)  dentro do mesmo mapa
        penalidade_de_mapas   = |map_id(n) - map_id(goal)| * portal_cost

    A penalidade garante que nós em mapas mais longe do destino recebam
    um custo estimado maior, sem superestimar (admissibilidade mantida
    desde que portal_cost ≤ custo real de cruzar um portal).
    """

    def parse_node(node: str) -> tuple[int, int, int]:
        """
        Retorna (map_id, row, col) de um nó no formato 'M2:(3,4)'.
        Para nós simples '(3,4)' retorna (0, row, col).
        """
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

    heuristica = {}
    for no in graph:
        no_map, no_r, no_c = parse_node(no)

        # Distância euclidiana até a posição do goal (dentro do espaço 2D)
        dist_espacial = ((no_r - goal_r) ** 2 + (no_c - goal_c) ** 2) ** 0.5

        # Penalidade proporcional à diferença de mapas ainda a atravessar
        mapas_restantes = abs(no_map - goal_map)
        penalidade      = mapas_restantes * portal_cost

        heuristica[no] = dist_espacial + penalidade

    return heuristica