"""
algorithms/ida_star.py
======================
AIA* — A* Iterativo (Iterative Deepening A*).

Como ativar
-----------
1. Implemente a lógica abaixo.
2. Em algorithms/__init__.py:
   - Descomente: from algorithms.ida_star import search as ida_star_search
   - Substitua:  'AIA* (A* Iterativo)': _stub_search  →  ida_star_search
"""

from search_result import SearchResult


def search(start: str, goal: str, graph: dict,
           heuristic: dict = None, depth_limit: int = None) -> SearchResult:
    """
    heuristic : dict {estado: valor_h} — admissível e consistente.
    """
    # ── TODO: implemente aqui ─────────────────────────────────────────────────
    raise NotImplementedError('IDA* ainda não implementado.')
