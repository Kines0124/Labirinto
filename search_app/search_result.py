"""
search_result.py
================
Define o tipo de retorno padrão de todos os algoritmos de busca.

Todo algoritmo implementado deve retornar um SearchResult, garantindo
que a interface gráfica receba sempre os mesmos campos independentemente
do método utilizado.
"""

from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """
    Resultado padronizado de uma busca.

    Atributos
    ---------
    path : list[str]
        Lista de estados do caminho encontrado (vazia se não houver solução).
        Exemplo: ['A', 'B', 'D', 'G']

    cost : float
        Custo total acumulado do caminho.

    nodes_expanded : int
        Quantidade de nós expandidos durante a busca.

    depth : int
        Profundidade da solução (len(path) - 1).

    found : bool
        True se um caminho foi encontrado. Derivado automaticamente de `path`.
    """
    path:           list[str] = field(default_factory=list)
    cost:           float     = 0.0
    nodes_expanded: int       = 0
    depth:          int       = 0

    @property
    def found(self) -> bool:
        return len(self.path) > 0

    def to_dict(self) -> dict:
        """Compatibilidade com código legado que espera dicionário."""
        return {
            'path':           self.path,
            'cost':           self.cost,
            'nodes_expanded': self.nodes_expanded,
            'depth':          self.depth,
        }
