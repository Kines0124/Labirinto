"""
config.py
=========
Centraliza toda a configuração do problema e da interface.
O mapa é um grid 15x15 onde 0 = livre e 1 = parede.
O GRAPH é gerado automaticamente a partir do grid.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
#  MAPA 15x15  (0 = livre, 1 = parede)
#  M[linha][coluna] — origem (0,0) no canto superior esquerdo
# ─────────────────────────────────────────────────────────────────────────────
GRID_ROWS = 15
GRID_COLS = 15

GRID_MAP: list[list[int]] = [
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
]


# ─────────────────────────────────────────────────────────────────────────────
#  PESOS DAS CÉLULAS  (apenas células livres são relevantes)
#  Custo de mover PARA aquela célula. Paredes são ignoradas.
#  Use 0.0 para células sem peso definido (fallback = 1.0 em _build_graph).
# ─────────────────────────────────────────────────────────────────────────────
GRID_WEIGHTS: list[list[float]] = [
    [1.0, 1.0, 1.0, 0.0, 5.0, 2.0, 2.0, 3.0, 5.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [5.0, 0.0, 3.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0],
    [1.0, 0.0, 2.0, 5.0, 1.0, 3.0, 3.0, 0.0, 1.0, 1.0, 1.0, 3.0, 0.0, 1.0, 0.0],
    [5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 1.0, 0.0],
    [3.0, 2.0, 2.0, 2.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 2.0, 1.0, 0.0],
    [0.0, 0.0, 1.0, 1.0, 0.0, 2.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0],
    [1.0, 0.0, 3.0, 5.0, 3.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 2.0, 2.0, 1.0, 1.0],
    [2.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 2.0, 3.0, 3.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    [1.0, 1.0, 1.0, 0.0, 2.0, 2.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 3.0, 0.0, 2.0],
    [0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 2.0, 0.0, 0.0, 1.0, 0.0, 1.0],
    [1.0, 2.0, 1.0, 1.0, 1.0, 0.0, 3.0, 3.0, 1.0, 1.0, 2.0, 0.0, 1.0, 1.0, 1.0],
    [1.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0],
    [1.0, 1.0, 2.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 0.0, 3.0, 1.0],
]
# Valores de referência de custo:
#   1.0 → terreno normal
#   2.0 → terreno difícil  (ex: água rasa, areia)
#   3.0 → terreno pesado   (ex: pântano, mato)
#   5.0 → terreno crítico  (quase intransponível, mas possível)
#   0.0 em célula livre    → fallback para 1.0 (usado em paredes, ignorado)


# ─────────────────────────────────────────────────────────────────────────────
#  CONVERSÃO AUTOMÁTICA: GRID → GRAPH
#  Nó  = "(linha,col)"
#  Custo de mover para (nr,nc) = GRID_WEIGHTS[nr][nc] (mínimo 1.0)
#  Vizinhos: 4 direções (cima, baixo, esquerda, direita)
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
            if grid[r][c] == 1:          # parede — não entra no grafo
                continue
            neighbors: list[tuple[str, float]] = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                    cost = weights[nr][nc] or 1.0   # 0.0 → fallback 1.0
                    neighbors.append((node(nr, nc), cost))
            graph[node(r, c)] = neighbors
    return graph


GRAPH: dict[str, list[tuple[str, float]]] = _build_graph(GRID_MAP, GRID_WEIGHTS)
STATES: list[str] = list(GRAPH.keys())

# Start = (0,0)  /  Goal = (14,14)
START_NODE: str = "(0,0)"
GOAL_NODE:  str = "(14,14)"


# ─────────────────────────────────────────────────────────────────────────────
#  POSIÇÕES VISUAIS — derivadas do grid (usadas pelo canvas)
# ─────────────────────────────────────────────────────────────────────────────
NODE_POSITIONS: dict[str, tuple[int, int]] = {
    f"({r},{c})": (c, r)
    for r in range(GRID_ROWS)
    for c in range(GRID_COLS)
    if GRID_MAP[r][c] == 0
}


# ─────────────────────────────────────────────────────────────────────────────
#  MÉTODOS DE BUSCA DISPONÍVEIS
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


# ─────────────────────────────────────────────────────────────────────────────
#  PALETA DE CORES
# ─────────────────────────────────────────────────────────────────────────────
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

    # tiles — livres por peso
    'tile_free':       '#252838',   # peso 1 (normal)
    'tile_w2':         '#2A2510',   # peso 2 (difícil)   — tom âmbar escuro
    'tile_w3':         '#1E1A0A',   # peso 3 (pesado)    — tom marrom escuro
    'tile_w5':         '#2A100A',   # peso 5 (crítico)   — tom vermelho escuro
    'tile_wall':       '#0D0F1A',
    'tile_border':     '#1E2035',

    # texto de peso dentro do tile
    'weight_normal':   '#3A3E55',   # peso 1 — sutil
    'weight_medium':   '#8A7A30',   # peso 2
    'weight_heavy':    '#6A4A18',   # peso 3
    'weight_critical': '#8A2020',   # peso 5

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


# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAÇÕES DA JANELA
# ─────────────────────────────────────────────────────────────────────────────
WINDOW = {
    'title':      'Busca em Grade — Visualizador',
    'width':      1100,
    'height':     700,
    'min_width':  900,
    'min_height': 620,
}