"""
algorithms/greedy.py
====================
Busca Gulosa (Greedy Best-First Search).

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.greedy import search as greedy_search
   - Substitua:  'Greedy Best-First': _stub_search  →  greedy_search
"""

from search_result import SearchResult


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
    """
    heuristic : dict {estado: valor_h} — distância estimada ao objetivo.
                Obrigatório para este algoritmo.
    """
    # ── TODO: implemente aqui ─────────────────────────────────────────────────
    raise NotImplementedError('Greedy ainda não implementado.')
