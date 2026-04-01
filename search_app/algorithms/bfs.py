"""
algorithms/bfs.py
=================
Busca em Amplitude (BFS).
Delega para BuscaNP.amplitude_grafo — nenhum código do algoritmo vive aqui.
"""

from algorithms.BuscaNP import buscaNP
from search_result import SearchResult
from algorithms.conversor import Conversor



# ── funções de conversão/adaptação ───────────────────────────────────────────
# Necessárias porque config.GRAPH usa formato diferente do esperado por buscaNP.
#
# config.GRAPH : {'A': [('B', 1), ('C', 4)], ...}
#   buscaNP espera:
#     nos   = ['A', 'B', 'C', ...]          (lista ordenada de estados)
#     grafo = [[idx_viz, ...], [idx_viz, ...], ...]  (índices dos vizinhos)


# ── função obrigatória chamada pelo REGISTRY ──────────────────────────────────

def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:

    nos, grafo = Conversor.converter_grafo(graph)

    # chamada direta ao método original — sem modificações
    caminho = buscaNP().amplitude_grafo(start, goal, nos, grafo)

    if caminho is None:
        return SearchResult()

    return SearchResult(
        path=caminho,
        cost= Conversor.calcular_custo(caminho, graph),
        nodes_expanded=0,
        depth=len(caminho) - 1,
    )