"""
config.py
=========
Centraliza toda a configuração do problema e da interface.

O mapa é sempre gerado proceduralmente via Kruskal (8×8 lógico → 15×15 grid).
Para reproduzir um labirinto específico, defina MAZE_SEED como inteiro.
Para regenerar em tempo de execução, chame config.regenerate_maze().
"""

from __future__ import annotations
from typing import Optional
from maze_generator import generate_kruskal_maze, maze_to_config_format

# ─────────────────────────────────────────────────────────────────────────────
# Parâmetros de geração
# ─────────────────────────────────────────────────────────────────────────────

# Dimensões lógicas — grid expandido resultante: (2*8-1) × (2*8-1) = 15×15
MAZE_LOGICAL_ROWS: int    = 8
MAZE_LOGICAL_COLS: int    = 8
MAZE_SEED: Optional[int]  = None   # None = aleatório; ex.: 42 para fixo


# ─────────────────────────────────────────────────────────────────────────────
# Construção do grafo
# ─────────────────────────────────────────────────────────────────────────────

def _build_graph(
    grid: list[list[int]],
    weights: list[list[float]],
) -> dict[str, list[tuple[str, float]]]:
    rows, cols = len(grid), len(grid[0])
    graph: dict[str, list[tuple[str, float]]] = {}

    def node(r: int, c: int) -> str:
        return f"({r},{c})"

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                continue
            neighbors: list[tuple[str, float]] = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                    cost = weights[nr][nc] or 1.0
                    neighbors.append((node(nr, nc), cost))
            graph[node(r, c)] = neighbors
    return graph


# ─────────────────────────────────────────────────────────────────────────────
# Geração inicial + regeneração em tempo de execução
# ─────────────────────────────────────────────────────────────────────────────

def _apply(result) -> None:
    """Aplica um MazeResult nos globais deste módulo."""
    import sys
    m = sys.modules[__name__]
    gm, gw, gr, gc = maze_to_config_format(result)
    m.GRID_MAP       = gm
    m.GRID_WEIGHTS   = gw
    m.GRID_ROWS      = gr
    m.GRID_COLS      = gc
    m.ACTIVE_SEED    = result.seed
    m.TERRAIN_MAP    = result.terrain_map
    m.GRAPH          = _build_graph(gm, gw)
    m.STATES         = list(m.GRAPH.keys())
    m.START_NODE     = "(0,0)"
    m.GOAL_NODE      = f"({gr - 1},{gc - 1})"
    m.NODE_POSITIONS = {
        f"({r},{c})": (c, r)
        for r in range(gr)
        for c in range(gc)
        if gm[r][c] == 0
    }


def regenerate_maze(seed: Optional[int] = None) -> None:
    """
    Regera o labirinto e atualiza todos os globais deste módulo.

        import config
        config.regenerate_maze()        # seed aleatória
        config.regenerate_maze(seed=42) # reproduzível
    """
    _apply(generate_kruskal_maze(
        rows=MAZE_LOGICAL_ROWS,
        cols=MAZE_LOGICAL_COLS,
        seed=seed,
    ))


# ─────────────────────────────────────────────────────────────────────────────
# Placeholders — preenchidos imediatamente por _apply()
# ─────────────────────────────────────────────────────────────────────────────

GRID_MAP:       list[list[int]]   = []
GRID_WEIGHTS:   list[list[float]] = []
GRID_ROWS:      int               = 0
GRID_COLS:      int               = 0
ACTIVE_SEED:    Optional[int]     = None
TERRAIN_MAP                       = None
GRAPH:          dict              = {}
STATES:         list[str]         = []
START_NODE:     str               = "(0,0)"
GOAL_NODE:      str               = "(14,14)"
NODE_POSITIONS: dict              = {}

_apply(generate_kruskal_maze(
    rows=MAZE_LOGICAL_ROWS,
    cols=MAZE_LOGICAL_COLS,
    seed=MAZE_SEED,
))


# ─────────────────────────────────────────────────────────────────────────────
# Configurações de UI
# ─────────────────────────────────────────────────────────────────────────────

SEARCH_METHODS: list[str] = [
    'Amplitude (BFS)',
    'Profundidade (DFS)',
    'Profundidade Limitada',
    'Aprofundamento Iterativo (IDDFS)',
    'Bidirecional',
    'Custo Uniforme (UCS)',
    'Greedy Best-First',
    'A* (A-estrela)',
    'AIA* (A* Iterativo)',
]

COLORS: dict[str, str] = {
    'bg':              '#1A1C2C',
    'panel':           '#1A1C2C',
    'panel_border':    '#2A2D40',

    'accent':          '#4F8EF7',
    'accent2':         '#A259FF',
    'success':         '#3ECFAA',
    'warning':         '#F7C948',
    'danger':          '#F75F5F',

    'text':            '#E8ECF8',
    'text_dim':        '#8890AA',

    # tiles por terreno
    'tile_free':       '#252838',   # plains   peso 1
    'tile_w2':         '#1A2010',   # forest   peso 2
    'tile_w3':         '#1A180A',   # swamp    peso 3
    'tile_w5':         '#251008',   # mountain peso 5
    'tile_wall':       '#0D0F1A',
    'tile_border':     '#1E2035',

    # texto de peso
    'weight_normal':   '#3A3E55',
    'weight_medium':   '#8A7A30',
    'weight_heavy':    '#6A4A18',
    'weight_critical': '#8A2020',

    # nós especiais
    'node_start':      '#1C3A5E',
    'node_goal':       '#1C3C2E',
    'node_path':       '#2D2040',
    'node_default':    '#252838',

    'node_glow_start': '#4F8EF7',
    'node_glow_goal':  '#3ECFAA',
    'node_glow_path':  '#A259FF',

    # arestas
    'edge_default':    '#2A2E45',
    'edge_path':       '#A259FF',
    'edge_glow':       '#6030A0',

    'grid':            '#151820',
}

WINDOW = {
    'title':      'Busca em Grade — Visualizador',
    'width':      1100,
    'height':     700,
    'min_width':  900,
    'min_height': 620,
}