"""
algorithms/astar.py
===================
A* (A-estrela).

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.astar import search as astar_search
   - Substitua:  'A* (A-estrela)': _stub_search  →  astar_search
"""

from search_result import SearchResult


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
    """
    heuristic : dict {estado: valor_h} — admissível e consistente.
    """
    # ── TODO: implemente aqui ─────────────────────────────────────────────────
    raise NotImplementedError('A* ainda não implementado.')
