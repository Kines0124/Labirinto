"""
algorithms/__init__.py
======================
Registro central dos algoritmos de busca.

Para ativar um algoritmo implementado:
  1. Descomente o import correspondente abaixo.
  2. Substitua _stub_search pela função importada no REGISTRY.
"""

from search_result import SearchResult

# ── imports dos algoritmos ────────────────────────────────────────────────────

from algorithms.bfs      import search as bfs_search      
from algorithms.dfs      import search as dfs_search
from algorithms.dls      import search as dls_search
from algorithms.iddfs    import search as iddfs_search
from algorithms.bidi     import search as bidi_search
from algorithms.ucs      import search as ucs_search
from algorithms.greedy   import search as greedy_search
from algorithms.astar    import search as astar_search
from algorithms.ida_star import search as ida_star_search


# ── registro: nome do método → função ────────────────────────────────────────

REGISTRY: dict[str, callable] = {
    'Amplitude (BFS)':                  bfs_search,     # ativo
    'Profundidade (DFS)':               dfs_search,   # TODO: trocar por dfs_search
    'Profundidade Limitada':            dls_search,   # TODO: trocar por dls_search
    'Aprofundamento Iterativo (IDDFS)': iddfs_search,   # TODO: trocar por iddfs_search
    'Bidirecional':                     bidi_search,   # TODO: trocar por bidi_search
    'Custo Uniforme (UCS)':             ucs_search,   # TODO: trocar por ucs_search
    'Greedy Best-First':                greedy_search,   # TODO: trocar por greedy_search
    'A* (A-estrela)':                   astar_search,   # TODO: trocar por astar_search
    'AIA* (A* Iterativo)':              ida_star_search   # TODO: trocar por ida_star_search
}


def run_search(method: str, start: str, goal: str,
               graph: dict, heuristic: dict,
               depth_limit: int = 3) -> SearchResult:
    fn = REGISTRY.get(method)
    if fn is None:
        print(f'[AVISO] Método "{method}" não encontrado no registro.')
        return SearchResult()

    return fn(
        start=start,
        goal=goal,
        graph=graph,
        heuristic=None,
        depth_limit=depth_limit,
    )