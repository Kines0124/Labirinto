"""
config.py
=========
Centraliza toda a configuração do problema e da interface.
Edite este arquivo para adaptar o grafo, heurísticas e aparência visual
sem precisar tocar no código da UI ou dos algoritmos.
"""

# ─────────────────────────────────────────────────────────────────────────────
#  GRAFO DO PROBLEMA
#  Formato: {estado: [(vizinho, custo), ...]}
# ─────────────────────────────────────────────────────────────────────────────
GRAPH: dict[str, list[tuple[str, int | float]]] = {
    'A': [('B', 1), ('C', 4)],
    'B': [('A', 1), ('D', 2), ('E', 5)],
    'C': [('A', 4), ('F', 3)],
    'D': [('B', 2), ('G', 1)],
    'E': [('B', 5), ('G', 2)],
    'F': [('C', 3), ('H', 2)],
    'G': [('D', 1), ('E', 2), ('I', 3)],
    'H': [('F', 2), ('I', 1)],
    'I': [('G', 3), ('H', 1)],
}

# Lista de estados derivada do grafo (ordem alfabética)
STATES: list[str] = sorted(GRAPH.keys())

# ─────────────────────────────────────────────────────────────────────────────
#  HEURÍSTICA
#  Distância estimada de cada estado ao objetivo.
#  Usada por: Greedy Best-First, A*, AIA*
# ─────────────────────────────────────────────────────────────────────────────
HEURISTIC: dict[str, int | float] = {
    'A': 7, 'B': 6, 'C': 5, 'D': 4,
    'E': 3, 'F': 4, 'G': 2, 'H': 2, 'I': 0,
}

# ─────────────────────────────────────────────────────────────────────────────
#  POSIÇÕES VISUAIS DOS NÓS
#  Coordenadas (x, y) para renderização no canvas.
#  Ajuste conforme o layout do seu problema.
# ─────────────────────────────────────────────────────────────────────────────
NODE_POSITIONS: dict[str, tuple[int, int]] = {
    'A': (120,  80),
    'B': (240, 180),
    'C': (120, 280),
    'D': (360, 120),
    'E': (360, 240),
    'F': (120, 380),
    'G': (480, 180),
    'H': (240, 400),
    'I': (480, 330),
}

# ─────────────────────────────────────────────────────────────────────────────
#  MÉTODOS DE BUSCA DISPONÍVEIS
#  A ordem aqui define a ordem no dropdown da interface.
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
    'bg':           '#3A3E3B',  # fundo principal
    'panel':        '#3A3E3B',  # painéis laterais
    'panel_border': '#000000',  # borda dos painéis
    'accent':       '#4F8EF7',  # azul principal
    'accent2':      '#A259FF',  # roxo secundário
    'success':      '#3ECFAA',  # verde/teal
    'warning':      '#F7C948',  # amarelo
    'danger':       '#F75F5F',  # vermelho
    'text':         '#E8ECF8',  # texto principal
    'text_dim':     '#FFFFFF',  # texto secundário
    'node_default': '#1E2235',  # nó padrão
    'node_start':   '#1C3A5E',  # nó inicial
    'node_goal':    '#1C3C2E',  # nó objetivo
    'node_path':    '#2D2040',  # nó no caminho
    'edge_default': '#2A2E45',  # aresta padrão
    'edge_path':    '#A259FF',  # aresta no caminho
    'grid':         '#151928',  # linhas da grade de fundo
    'node_glow_start': '#1A4A8A',
    'node_glow_goal':  '#1A5040',
    'node_glow_path':  '#3D2070',
    'edge_glow':       '#6030A0',
}

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAÇÕES DA JANELA
# ─────────────────────────────────────────────────────────────────────────────
WINDOW = {
    'title':      'Busca em Árvore — Visualizador',
    'width':      1100,
    'height':     700,
    'min_width':  900,
    'min_height': 620,
}
