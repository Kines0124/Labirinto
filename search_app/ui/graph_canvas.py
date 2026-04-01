"""
ui/graph_canvas.py
==================
Widget de canvas responsável exclusivamente pela renderização do grafo.
Não contém lógica de busca nem de controle de formulário.
"""

import tkinter as tk
from config import COLORS, GRAPH, NODE_POSITIONS, STATES


class GraphCanvas(tk.Canvas):
    """
    Canvas que desenha o grafo do problema e destaca visualmente
    o caminho encontrado por um algoritmo de busca.

    Uso
    ---
    canvas = GraphCanvas(parent)
    canvas.pack(fill='both', expand=True)
    canvas.render(path=['A', 'B', 'G'], start='A', goal='G')
    canvas.render()   # limpa o destaque
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], highlightthickness=0, **kwargs)
        self._fonts: dict = {}   # injetado pelo app principal após criação dos fonts
        self.bind('<Configure>', lambda _e: self.render())

    def set_fonts(self, fonts: dict):
        """Recebe as fontes do app principal (evita recriar Font objects)."""
        self._fonts = fonts

    def render(self, path: list[str] = None,
               start: str = None, goal: str = None):
        """
        Redesenha o grafo completo.

        Parâmetros
        ----------
        path  : lista de nós que compõem o caminho a destacar
        start : nó inicial (coloração especial)
        goal  : nó objetivo (coloração especial)
        """
        self.delete('all')

        path  = path  or []
        start = start or (STATES[0] if STATES else '')
        goal  = goal  or (STATES[-1] if STATES else '')

        path_edges = set()
        for i in range(len(path) - 1):
            path_edges.add((path[i], path[i + 1]))
            path_edges.add((path[i + 1], path[i]))

        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480

        scale = self._calc_scale(cw, ch)

        def pos(node):
            nx, ny = NODE_POSITIONS[node]
            return 20 + nx * scale, 20 + ny * scale

        self._draw_grid(cw, ch)
        self._draw_edges(pos, path_edges)
        self._draw_nodes(pos, path, path_edges, start, goal)

    # ── métodos internos de desenho ──────────────────────────────────────────

    def _calc_scale(self, cw: int, ch: int) -> float:
        all_x = [p[0] for p in NODE_POSITIONS.values()]
        all_y = [p[1] for p in NODE_POSITIONS.values()]
        mx = max(all_x) + 60
        my = max(all_y) + 60
        sx = (cw - 40) / max(mx, 1)
        sy = (ch - 40) / max(my, 1)
        return min(sx, sy, 1.4)

    def _draw_grid(self, cw: int, ch: int):
        for xi in range(0, cw, 40):
            self.create_line(xi, 0, xi, ch, fill=COLORS['grid'], width=1)
        for yi in range(0, ch, 40):
            self.create_line(0, yi, cw, yi, fill=COLORS['grid'], width=1)

    def _draw_edges(self, pos_fn, path_edges: set):
        f_section = self._fonts.get('section')
        drawn = set()

        for node, neighbors in GRAPH.items():
            x1, y1 = pos_fn(node)
            for nb, cost in neighbors:
                key = tuple(sorted([node, nb]))
                if key in drawn:
                    continue
                drawn.add(key)

                x2, y2 = pos_fn(nb)
                is_path = (node, nb) in path_edges
                clr = COLORS['edge_path'] if is_path else COLORS['edge_default']
                w   = 3 if is_path else 1.5

                if is_path:
                    self.create_line(x1, y1, x2, y2,
                                     fill=COLORS['edge_glow'],
                                     width=w + 4, smooth=True)
                self.create_line(x1, y1, x2, y2, fill=clr,
                                 width=w, smooth=True)

                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                self.create_text(mx + 2, my + 2, text=str(cost),
                                 font=f_section, fill=COLORS['grid'])
                self.create_text(mx, my, text=str(cost),
                                 font=f_section,
                                 fill=COLORS['warning'] if is_path else COLORS['text_dim'])

    def _draw_nodes(self, pos_fn, path: list, path_edges: set,
                    start: str, goal: str):
        f_node    = self._fonts.get('node')
        f_section = self._fonts.get('section')
        scale     = self._calc_scale(self.winfo_width() or 600,
                                     self.winfo_height() or 480)
        r = max(18, int(22 * scale))

        for node in GRAPH:
            x, y = pos_fn(node)
            in_path = node in path

            fill, ring, glow, tf = self._node_style(node, in_path, start, goal)

            if glow:
                self.create_oval(x-r-6, y-r-6, x+r+6, y+r+6,
                                 fill='', outline=glow, width=4)
            self.create_oval(x-r, y-r, x+r, y+r,
                             fill=fill, outline=ring, width=2)
            self.create_text(x, y, text=node, font=f_node, fill=tf)

            if in_path:
                idx = path.index(node)
                bx, by = x + r - 4, y - r + 4
                self.create_oval(bx-8, by-8, bx+8, by+8,
                                 fill=COLORS['accent2'], outline='')
                self.create_text(bx, by, text=str(idx),
                                 font=f_section, fill='#ffffff')

    @staticmethod
    def _node_style(node: str, in_path: bool,
                    start: str, goal: str) -> tuple:
        if node == start:
            return (COLORS['node_start'], COLORS['accent'],
                    COLORS['node_glow_start'], COLORS['accent'])
        if node == goal:
            return (COLORS['node_goal'], COLORS['success'],
                    COLORS['node_glow_goal'], COLORS['success'])
        if in_path:
            return (COLORS['node_path'], COLORS['accent2'],
                    COLORS['node_glow_path'], COLORS['accent2'])
        return (COLORS['node_default'], COLORS['panel_border'],
                None, COLORS['text'])
