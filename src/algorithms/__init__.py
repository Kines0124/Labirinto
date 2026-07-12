"""
algorithms/__init__.py
======================
Central registry of search algorithms.
"""


from search_result import SearchResult

# ── algorithm imports ──────────────────────────────────────────────────────

from algorithms.bfs      import search as bfs_search      
from algorithms.dfs      import search as dfs_search
from algorithms.dls      import search as dls_search
from algorithms.iddfs    import search as iddfs_search
from algorithms.bidi     import search as bidi_search
from algorithms.ucs      import search as ucs_search
from algorithms.greedy   import search as greedy_search
from algorithms.astar    import search as astar_search
from algorithms.ida_star import search as ida_star_search


# ── registry: method name → function ────────────────────────────────────────

REGISTRY: dict[str, callable] = {
    'Amplitude (BFS)':                  bfs_search,     
    'Profundidade (DFS)':               dfs_search,   
    'Profundidade Limitada':            dls_search,   
    'Aprofundamento Iterativo (IDDFS)': iddfs_search,   
    'Bidirecional':                     bidi_search,   
    'Custo Uniforme (UCS)':             ucs_search,   
    'Greedy Best-First':                greedy_search,   
    'A* (A-estrela)':                   astar_search, 
    'AIA* (A* Iterativo)':              ida_star_search   
}


HEURISTIC_METHODS = {'Greedy Best-First', 'A* (A-estrela)', 'AIA* (A* Iterativo)'}

def run_search(method: str, start: str, goal: str,
               graph: dict, heuristic: dict,
               depth_limit: int = 3,
               heuristic_name: str = 'manhattan') -> SearchResult:
    """Localiza o algoritmo no registro e executa a busca com os parâmetros adequados."""
    fn = REGISTRY.get(method)
    if fn is None:
        print(f'[AVISO] Método "{method}" não encontrado no registro.')
        return SearchResult()

    kwargs = dict(
        start=start,
        goal=goal,
        graph=graph,
        heuristic=None,
        depth_limit=depth_limit,
    )
    if method in HEURISTIC_METHODS:
        kwargs['heuristic_name'] = heuristic_name

    return fn(**kwargs)