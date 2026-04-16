"""
ui/graph_canvas.py
==================
Widget de canvas responsável exclusivamente pela renderização do mapa em grid.
Renderiza um grid 15x15 com células livres e paredes.
Tilesets podem substituir as cores mais tarde — veja _draw_tile().
"""

from __future__ import annotations
import tkinter as tk
from config import COLORS, GRID_MAP, GRID_WEIGHTS, GRID_ROWS, GRID_COLS, START_NODE, GOAL_NODE


def _node_to_rc(node: str) -> tuple[int, int]:
    """'(r,c)' → (r, c)"""
    inner = node.strip("()")
    r, c = inner.split(",")
    return int(r), int(c)


class GraphCanvas(tk.Canvas):
    """
    Canvas que renderiza o mapa como um grid de tiles.

    Uso
    ---
    canvas = GraphCanvas(parent)
    canvas.pack(fill='both', expand=True)
    canvas.render(path=['(0,0)', '(0,1)', ...], start='(0,0)', goal='(14,14)')
    canvas.render()   # limpa destaque
    """

    # tamanho mínimo de célula em px
    _MIN_CELL = 20
    _MAX_CELL = 48

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'],
                         highlightthickness=0, **kwargs)
        self._fonts: dict = {}
        self.bind('<Configure>', lambda _e: self.render())

    def set_fonts(self, fonts: dict):
        self._fonts = fonts

    # ── API pública ──────────────────────────────────────────────────────────

    def render(self, path: list[str] = None,
               start: str = None, goal: str = None):
        """Redesenha o mapa completo."""
        self.delete('all')

        path  = path  or []
        start = start or START_NODE
        goal  = goal  or GOAL_NODE

        path_set = set(path)

        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480

        cell = self._cell_size(cw, ch)
        ox, oy = self._origin(cw, ch, cell)

        self._draw_background(cw, ch)

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                node = f"({r},{c})"
                wall = GRID_MAP[r][c] == 1
                in_path = node in path_set
                weight = GRID_WEIGHTS[r][c] or 1.0
                self._draw_tile(r, c, cell, ox, oy,
                                wall=wall,
                                in_path=in_path,
                                is_start=(node == start),
                                is_goal=(node == goal),
                                weight=weight)

        # desenha caminho por cima (setas/linha)
        if len(path) > 1:
            self._draw_path_overlay(path, cell, ox, oy)

        # índices de ordem no caminho
        self._draw_path_indices(path, cell, ox, oy)

    # ── layout ───────────────────────────────────────────────────────────────

    def _cell_size(self, cw: int, ch: int) -> int:
        sx = (cw - 40) // GRID_COLS
        sy = (ch - 40) // GRID_ROWS
        return max(self._MIN_CELL, min(self._MAX_CELL, sx, sy))

    def _origin(self, cw: int, ch: int, cell: int) -> tuple[int, int]:
        total_w = cell * GRID_COLS
        total_h = cell * GRID_ROWS
        ox = (cw - total_w) // 2
        oy = (ch - total_h) // 2
        return ox, oy

    def _tile_rect(self, r: int, c: int, cell: int,
                   ox: int, oy: int) -> tuple[int, int, int, int]:
        x1 = ox + c * cell
        y1 = oy + r * cell
        return x1, y1, x1 + cell, y1 + cell

    def _tile_center(self, r: int, c: int, cell: int,
                     ox: int, oy: int) -> tuple[float, float]:
        x1, y1, x2, y2 = self._tile_rect(r, c, cell, ox, oy)
        return (x1 + x2) / 2, (y1 + y2) / 2

    # ── desenho ──────────────────────────────────────────────────────────────

    def _draw_background(self, cw: int, ch: int):
        self.create_rectangle(0, 0, cw, ch, fill=COLORS['bg'], outline='')

    def _draw_tile(self, r: int, c: int, cell: int, ox: int, oy: int,
                   wall: bool, in_path: bool,
                   is_start: bool, is_goal: bool,
                   weight: float = 1.0):
        """
        Desenha uma célula do grid.

        Troca futura por tileset:
            substituir create_rectangle por
            self.create_image(x1, y1, anchor='nw', image=TILE_IMG[tipo])
        """
        x1, y1, x2, y2 = self._tile_rect(r, c, cell, ox, oy)
        pad = 1

        if wall:
            self.create_rectangle(
                x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                fill=COLORS['tile_wall'], outline=COLORS['tile_border'], width=1
            )
            self.create_line(x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                             fill=COLORS['tile_border'], width=1)
            self.create_line(x2 - pad, y1 + pad, x1 + pad, y2 - pad,
                             fill=COLORS['tile_border'], width=1)
            return

        # ── cor base pelo peso (só para células não destacadas) ──
        if is_start:
            fill = COLORS['node_start']
            glow = COLORS['node_glow_start']
        elif is_goal:
            fill = COLORS['node_goal']
            glow = COLORS['node_glow_goal']
        elif in_path:
            fill = COLORS['node_path']
            glow = COLORS['node_glow_path']
        else:
            glow = None
            if weight >= 5.0:
                fill = COLORS['tile_w5']
            elif weight >= 3.0:
                fill = COLORS['tile_w3']
            elif weight >= 2.0:
                fill = COLORS['tile_w2']
            else:
                fill = COLORS['tile_free']

        self.create_rectangle(
            x1 + pad, y1 + pad, x2 - pad, y2 - pad,
            fill=fill,
            outline=COLORS['tile_border'] if not glow else glow,
            width=1 if not glow else 2
        )

        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        r_mark = max(4, cell // 5)

        if is_start:
            self._draw_marker(cx, cy, r_mark, COLORS['accent'], 'S')
        elif is_goal:
            self._draw_marker(cx, cy, r_mark, COLORS['success'], 'G')
        elif not in_path and cell >= 28:
            # exibe peso no canto superior esquerdo da célula
            self._draw_weight_label(x1, y1, weight)

    def _draw_marker(self, cx: float, cy: float, r: int,
                     color: str, label: str):
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=color, outline='')
        f = self._fonts.get('section')
        if f:
            self.create_text(cx, cy, text=label, font=f, fill='#ffffff')

    def _draw_weight_label(self, x1: float, y1: float, weight: float):
        """Exibe o peso no canto superior esquerdo da célula."""
        f = self._fonts.get('section')
        if not f:
            return
        text = str(int(weight)) if weight == int(weight) else str(weight)
        if weight >= 5.0:
            color = COLORS['weight_critical']
        elif weight >= 3.0:
            color = COLORS['weight_heavy']
        elif weight >= 2.0:
            color = COLORS['weight_medium']
        else:
            color = COLORS['weight_normal']
        self.create_text(x1 + 6, y1 + 6, text=text, font=f,
                         fill=color, anchor='nw')

    def _draw_path_overlay(self, path: list[str], cell: int,
                            ox: int, oy: int):
        """Linha conectando centros das células do caminho."""
        points = []
        for node in path:
            r, c = _node_to_rc(node)
            cx, cy = self._tile_center(r, c, cell, ox, oy)
            points.extend([cx, cy])

        if len(points) >= 4:
            # glow
            self.create_line(*points,
                             fill=COLORS['edge_glow'],
                             width=max(4, cell // 4),
                             smooth=True, joinstyle='round', capstyle='round')
            # linha principal
            self.create_line(*points,
                             fill=COLORS['edge_path'],
                             width=max(2, cell // 6),
                             smooth=True, joinstyle='round', capstyle='round')

    def _draw_path_indices(self, path: list[str], cell: int,
                            ox: int, oy: int):
        """Número de ordem sobre cada célula do caminho (exceto start/goal)."""
        f = self._fonts.get('section')
        if not f or cell < 28:   # muito pequeno pra caber texto
            return
        for idx, node in enumerate(path):
            if idx == 0 or idx == len(path) - 1:
                continue
            r, c = _node_to_rc(node)
            cx, cy = self._tile_center(r, c, cell, ox, oy)
            bx, by = cx + cell // 2 - 6, cy - cell // 2 + 6
            dot_r = 7
            self.create_oval(bx - dot_r, by - dot_r,
                             bx + dot_r, by + dot_r,
                             fill=COLORS['accent2'], outline='')
            self.create_text(bx, by, text=str(idx),
                             font=f, fill='#ffffff')