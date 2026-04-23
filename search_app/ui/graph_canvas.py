"""
ui/graph_canvas.py
==================
Widget de canvas responsável exclusivamente pela renderização do mapa em grid.
Renderiza um grid 15x15 com células livres (coloridas por terreno) e paredes.
Tilesets podem substituir as cores mais tarde — veja _draw_tile().
"""

from __future__ import annotations
from pathlib import Path
import tkinter as tk
import config
from config import COLORS, GRID_MAP, GRID_WEIGHTS, GRID_ROWS, GRID_COLS, \
                   START_NODE, GOAL_NODE
from PIL import Image, ImageTk  # pip install pillow


def _node_to_rc(node: str) -> tuple[int, int]:
    """'(r,c)' → (r, c)"""
    inner = node.strip("()")
    r, c = inner.split(",")
    return int(r), int(c)


# Mapeamento terreno → chave de cor em COLORS
_TERRAIN_COLOR: dict[str, str] = {
    'plains':   'tile_free',
    'forest':   'tile_w2',
    'swamp':    'tile_w3',
    'mountain': 'tile_w5',
}


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

    _MIN_CELL = 20
    _MAX_CELL = 48

    def __init__(self, parent, on_regenerate=None, **kwargs):
        super().__init__(parent, bg=COLORS['bg'],
                         highlightthickness=0, **kwargs)
        self._fonts: dict = {}
        self._on_regenerate = on_regenerate
        self.bind('<Configure>', lambda _e: self.render()) # remover depois 
        # SUBSTITUIR POR ISSO DEPOIS
        # self._tile_imgs: dict[str, ImageTk.PhotoImage] = {}  # ← adiciona
        # self.bind('<Configure>', lambda _e: self._reload_tiles() or self.render())  # ← troca
        
    def clear_path(self):
        self.render(path=[])

    def set_fonts(self, fonts: dict):
        self._fonts = fonts

    def _reload_tiles(self):
        """Redimensiona os tilesets para o cell size atual e cacheia."""
        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480
        cell = self._cell_size(cw, ch, config.GRID_ROWS, config.GRID_COLS)

        # só recarrega se o tamanho mudou
        if getattr(self, '_cached_cell', None) == cell:
            return
        self._cached_cell = cell

        _ROOT = Path(__file__).parent.parent  # sobe de ui/ para a raiz

        paths = {
            'plains':   _ROOT / 'assets' / 'tilesets' / 'plains.png',
            'forest':   _ROOT / 'assets' / 'tilesets' / 'forest.png',
            'swamp':    _ROOT / 'assets' / 'tilesets' / 'swamp.png',
            'mountain': _ROOT / 'assets' / 'tilesets' / 'mountain.png',
            'wall':     _ROOT / 'assets' / 'tilesets' / 'wall.png',
            'path':     _ROOT / 'assets' / 'tilesets' / 'path.png',
        }
        self._tile_imgs = {}
        for name, filepath in paths.items():
            img = Image.open(filepath).resize((cell, cell), Image.NEAREST) # Trocar pra Image.LANCZOS para alta resolução
            self._tile_imgs[name] = ImageTk.PhotoImage(img)

    # ── API pública ──────────────────────────────────────────────────────────

    def render(self, path: list[str] = None,
               start: str = None, goal: str = None):
        """Redesenha o mapa completo lendo os globais atuais de config."""
        self.delete('all')

        # Lê sempre do módulo para pegar o estado mais recente após regeneração
        grid_map     = config.GRID_MAP
        grid_weights = config.GRID_WEIGHTS
        grid_rows    = config.GRID_ROWS
        grid_cols    = config.GRID_COLS
        terrain_map  = config.TERRAIN_MAP

        path  = path  or []
        start = start or config.START_NODE
        goal  = goal  or config.GOAL_NODE

        path_set = set(path)

        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480

        cell = self._cell_size(cw, ch, grid_rows, grid_cols)
        ox, oy = self._origin(cw, ch, cell, grid_rows, grid_cols)

        self._draw_background(cw, ch)

        for r in range(grid_rows):
            for c in range(grid_cols):
                node   = f"({r},{c})"
                wall   = grid_map[r][c] == 1
                weight = grid_weights[r][c] or 1.0
                terrain = (terrain_map[r][c]
                           if terrain_map and not wall else None)
                self._draw_tile(
                    r, c, cell, ox, oy,
                    wall=wall,
                    in_path=(node in path_set),
                    is_start=(node == start),
                    is_goal=(node == goal),
                    weight=weight,
                    terrain=terrain,
                )

        if len(path) > 1:
            self._draw_path_overlay(path, cell, ox, oy)

        self._draw_path_indices(path, cell, ox, oy)

        if self._on_regenerate:
            self._draw_regen_button()

    # ── layout ───────────────────────────────────────────────────────────────

    def _cell_size(self, cw: int, ch: int,
                   grid_rows: int, grid_cols: int) -> int:
        sx = (cw - 40) // grid_cols
        sy = (ch - 40) // grid_rows
        return max(self._MIN_CELL, min(self._MAX_CELL, sx, sy))

    def _origin(self, cw: int, ch: int, cell: int,
                grid_rows: int, grid_cols: int) -> tuple[int, int]:
        ox = (cw - cell * grid_cols) // 2
        oy = (ch - cell * grid_rows) // 2
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
                   weight: float = 1.0, terrain=None):
        
        """
        Troca futura por tileset:
            substituir create_rectangle por
            self.create_image(x1, y1, anchor='nw', image=TILE_IMG[tipo])
        """
        x1, y1, x2, y2 = self._tile_rect(r, c, cell, ox, oy)
        pad = 1

        if wall:
            self.create_rectangle(
                x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                fill=COLORS['tile_wall'],
                outline=COLORS['tile_border'], width=1,
            )
            self.create_line(x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                             fill=COLORS['tile_border'], width=1)
            self.create_line(x2 - pad, y1 + pad, x1 + pad, y2 - pad,
                             fill=COLORS['tile_border'], width=1)
            return

        # ── cor base ──────────────────────────────────────────────────────
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
            # usa a cor do terreno se disponível, senão fallback por peso
            if terrain is not None:
                color_key = _TERRAIN_COLOR.get(terrain.name, 'tile_free')
                fill = COLORS[color_key]
            elif weight >= 5.0:
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
            width=1 if not glow else 2,
        )

        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        r_mark = max(4, cell // 5)

        if is_start:
            self._draw_marker(cx, cy, r_mark, COLORS['accent'], 'S')
        elif is_goal:
            self._draw_marker(cx, cy, r_mark, COLORS['success'], 'G')
        elif not in_path and cell >= 28:
            self._draw_weight_label(x1, y1, weight)

    # DESCOMENTAR ISSO AQUI E DELETAR O _draw_tile ANTERIOR

    # def _draw_tile(self, r, c, cell, ox, oy, wall, in_path,
    #            is_start, is_goal, weight, terrain=None):
    #     x1, y1, x2, y2 = self._tile_rect(r, c, cell, ox, oy)

    #     # ── resolve qual chave de tileset usar ──
    #     if wall:
    #         tile_key = 'wall'
    #     elif in_path and not is_start and not is_goal:
    #         tile_key = 'path'
    #     elif terrain is not None:
    #         tile_key = terrain.name          # 'plains', 'forest', etc.
    #     else:
    #         tile_key = 'plains'              # fallback

    #     # ── tenta renderizar com imagem, cai em retângulo se não tiver ──
    #     img = self._tile_imgs.get(tile_key)
    #     if img:
    #         self.create_image(x1, y1, anchor='nw', image=img)
    #     else:
    #         # fallback: comportamento atual com create_rectangle
    #         ...  # mantém o código de retângulo que já existe

    #     # marcadores S e G ficam por cima da imagem — não mudam
    #     if is_start:
    #         cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    #         self._draw_marker(cx, cy, max(4, cell // 5), COLORS['accent'], 'S')
    #     elif is_goal:
    #         cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    #         self._draw_marker(cx, cy, max(4, cell // 5), COLORS['success'], 'G')

    def _draw_marker(self, cx: float, cy: float, r: int,
                     color: str, label: str):
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=color, outline='')
        f = self._fonts.get('section')
        if f:
            self.create_text(cx, cy, text=label, font=f, fill='#ffffff')

    def _draw_weight_label(self, x1: float, y1: float, weight: float):
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
        points = []
        for node in path:
            r, c = _node_to_rc(node)
            cx, cy = self._tile_center(r, c, cell, ox, oy)
            points.extend([cx, cy])

        if len(points) >= 4:
            self.create_line(*points,
                             fill=COLORS['edge_glow'],
                             width=max(4, cell // 4),
                             smooth=True, joinstyle='round', capstyle='round')
            self.create_line(*points,
                             fill=COLORS['edge_path'],
                             width=max(2, cell // 6),
                             smooth=True, joinstyle='round', capstyle='round')

    def _draw_path_indices(self, path: list[str], cell: int,
                            ox: int, oy: int):
        f = self._fonts.get('section')
        if not f or cell < 28:
            return
        for idx, node in enumerate(path):
            if idx == 0 or idx == len(path) - 1:
                continue
            r, c = _node_to_rc(node)
            cx, cy = self._tile_center(r, c, cell, ox, oy)
            bx = cx + cell // 2 - 6
            by = cy - cell // 2 + 6
            dot_r = 7
            self.create_oval(bx - dot_r, by - dot_r,
                             bx + dot_r, by + dot_r,
                             fill=COLORS['accent2'], outline='')
            self.create_text(bx, by, text=str(idx),
                             font=f, fill='#ffffff')

    def _draw_regen_button(self):
        """Botão flutuante 'Novo Labirinto' no canto inferior direito."""
        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480

        bw, bh = 190, 32
        x1 = cw - bw - 12
        y1 = ch - bh - 12
        x2, y2 = x1 + bw, y1 + bh

        btn = self.create_rectangle(
            x1, y1, x2, y2,
            fill=COLORS['accent'],
            outline=COLORS['node_glow_start'], width=1,
            tags='regen_btn',
        )
        self.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text='⟳  Novo Labirinto',
            font=self._fonts.get('section'),
            fill='#ffffff',
            tags='regen_btn',
        )

        def on_enter(_e):
            self.itemconfig(btn, fill=COLORS['node_glow_start'])
            self.config(cursor='hand2')

        def on_leave(_e):
            self.itemconfig(btn, fill=COLORS['accent'])
            self.config(cursor='')

        self.tag_bind('regen_btn', '<Enter>',    on_enter)
        self.tag_bind('regen_btn', '<Leave>',    on_leave)
        self.tag_bind('regen_btn', '<Button-1>',
                      lambda _e: self._on_regenerate())