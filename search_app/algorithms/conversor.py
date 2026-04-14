class Conversor(object):

    def converter_grafo(graph: dict) -> tuple:
        nos   = sorted(graph.keys())
        grafo = [[viz for viz, _custo in graph[n]] for n in nos]
        return nos, grafo


    def calcular_custo(path: list, graph: dict) -> float:
        """Recalcula o custo real do caminho usando os pesos do config."""
        total = 0.0
        for i in range(len(path) - 1):
            total += dict(graph[path[i]]).get(path[i + 1], 1)
        return total
    
    @staticmethod
    def converter_grafo_ponderado(graph: dict) -> tuple:
        nos   = sorted(graph.keys())
        grafo = [graph[n] for n in nos]  # ja e lista de (estado, custo)
        return nos, grafo