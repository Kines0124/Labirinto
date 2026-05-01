"""
algorithms/conversor.py
===================
Helper para conversões de grafos ponderados e não ponderados.
Auxiliar para cálculo de custo.
"""


class Conversor(object):

    def converter_grafo(graph: dict) -> tuple:
        """Converte o grafo para uso de buscas não ponderadas."""
        nos   = sorted(graph.keys())
        grafo = [[viz for viz, _custo in graph[n]] for n in nos]
        return nos, grafo

    def calcular_custo(path: list, graph: dict) -> float:
        """Recalcula o custo real do caminho usando os pesos do config."""
        total = 0.0
        for i in range(len(path) - 1):
            total += dict(graph[path[i]]).get(path[i + 1], 1)
        return total

    def converter_grafo_ponderado(graph: dict) -> tuple:
        """Converte o grafo para uso de buscas ponderadas."""
        nos   = sorted(graph.keys())
        grafo = [graph[n] for n in nos]  
        return nos, grafo