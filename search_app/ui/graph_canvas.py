"""
ui/graph_canvas.py
==================
Widget de canvas responsável exclusivamente pela renderização do mapa em grid.
Renderiza um grid 15x15 com células livres (coloridas por terreno) e paredes.
Portais são destacados com uma cor especial (azul-ciano) e o símbolo ⊕.
"""

from __future__ import annotations
from pathlib import Path
import tkinter as tk
import config
from config import COLORS
from PIL import Image, ImageTk  # pip install pillow


def _node_to_rc(node: str) -> tuple[int, int]:
    """
    Converte um nó para (row, col).
    Aceita tanto "(r,c)"  quanto  "M2:(r,c)".
    """
    # Remove prefixo de mapa se existir
    if ':' in node:
        node = node.split(':', 1)[1]
    inner = node.strip('()')
    r, c = inner.split(',')
    return int(r), int(c)


def _node_map_id(node: str) -> int | None:
    """Retorna o id do mapa de um nó 'M{id}:(r,c)', ou None para modo simples."""
    if node.startswith('M') and ':' in node:
        try:
            return int(node.split(':')[0][1:])
        except ValueError:
            pass
    return None


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

    def __init__(self, parent, on_regenerate=None, on_node_picked=None,
                 on_map_nav=None, **kwargs):
        super().__init__(parent, bg=COLORS['bg'],
                         highlightthickness=0, **kwargs)
        self._fonts: dict = {}
        self._on_regenerate  = on_regenerate
        self._on_node_picked = on_node_picked
        self._on_map_nav     = on_map_nav   # callback(delta: int) — +1 ou -1
        self._pick_mode: str | None = None
        self.bind('<Configure>', lambda _e: self.render())
        self.bind('<Button-1>', self._on_canvas_click)

    def clear_path(self):
        self.render(path=[])

    def set_pick_mode(self, mode: str | None):
        """Ativa ('start'/'goal') ou desativa (None) o modo de seleção por clique."""
        self._pick_mode = mode
        self.config(cursor='crosshair' if mode else '')

    def _on_canvas_click(self, event):
        if not self._pick_mode:
            return

        grid_map  = config.GRID_MAP
        grid_rows = config.GRID_ROWS
        grid_cols = config.GRID_COLS

        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480
        cell = self._cell_size(cw, ch, grid_rows, grid_cols)
        ox, oy = self._origin(cw, ch, cell, grid_rows, grid_cols)

        c = (event.x - ox) // cell
        r = (event.y - oy) // cell

        if not (0 <= r < grid_rows and 0 <= c < grid_cols):
            return
        if grid_map[r][c] == 1:
            return

        # Formata o nó com ou sem prefixo de mapa
        if config.MULTIVERSE_MODE:
            node = f"M{config.ACTIVE_MAP_ID}:({r},{c})"
        else:
            node = f"({r},{c})"

        role = self._pick_mode
        self.set_pick_mode(None)

        if self._on_node_picked:
            self._on_node_picked(role, node)

    def set_fonts(self, fonts: dict):
        self._fonts = fonts

    def _reload_tiles(self):
        """Redimensiona os tilesets para o cell size atual e cacheia."""
        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480
        cell = self._cell_size(cw, ch, config.GRID_ROWS, config.GRID_COLS)

        if getattr(self, '_cached_cell', None) == cell:
            return
        self._cached_cell = cell

        _ROOT = Path(__file__).parent.parent
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
            img = Image.open(filepath).resize((cell, cell), Image.NEAREST)
            self._tile_imgs[name] = ImageTk.PhotoImage(img)

    # ── API pública ──────────────────────────────────────────────────────────

    def render(self, path: list[str] = None,
               start: str = None, goal: str = None):
        """Redesenha o mapa completo lendo os globais atuais de config."""
        self.delete('all')

        grid_map     = config.GRID_MAP
        grid_weights = config.GRID_WEIGHTS
        grid_rows    = config.GRID_ROWS
        grid_cols    = config.GRID_COLS
        terrain_map  = config.TERRAIN_MAP

        path  = path  or []
        start = start or config.START_NODE
        goal  = goal  or config.GOAL_NODE

        # Filtra o caminho para mostrar só nós do mapa ativo
        if config.MULTIVERSE_MODE:
            active_id = config.ACTIVE_MAP_ID
            path_set  = {
                _node_to_rc(n)
                for n in path
                if _node_map_id(n) == active_id
            }
            # Converte start/goal para (r,c) se forem do mapa ativo
            start_rc = _node_to_rc(start) if _node_map_id(start) == active_id else None
            goal_rc  = _node_to_rc(goal)  if _node_map_id(goal)  == active_id else None
        else:
            path_set = {_node_to_rc(n) for n in path}
            start_rc = _node_to_rc(start) if start else None
            goal_rc  = _node_to_rc(goal)  if goal  else None

        # Células que contêm portais no mapa ativo
        portal_cells: set[tuple[int, int]] = set()
        if config.MULTIVERSE_MODE and config.MULTIVERSE is not None:
            from multiverse import portal_cells_of_map
            portal_cells = portal_cells_of_map(config.MULTIVERSE,
                                               config.ACTIVE_MAP_ID)

        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480

        cell = self._cell_size(cw, ch, grid_rows, grid_cols)
        ox, oy = self._origin(cw, ch, cell, grid_rows, grid_cols)

        self._draw_background(cw, ch)

        for r in range(grid_rows):
            for c in range(grid_cols):
                wall    = grid_map[r][c] == 1
                weight  = grid_weights[r][c] or 1.0
                terrain = (terrain_map[r][c]
                           if terrain_map and not wall else None)
                rc = (r, c)
                self._draw_tile(
                    r, c, cell, ox, oy,
                    wall=wall,
                    in_path=(rc in path_set),
                    is_start=(start_rc == rc),
                    is_goal=(goal_rc  == rc),
                    is_portal=(rc in portal_cells and not wall),
                    weight=weight,
                    terrain=terrain,
                )

        # Path overlay apenas com nós do mapa ativo (coordenadas locais)
        if config.MULTIVERSE_MODE:
            local_path = [
                f"({r},{c})" for r, c in
                [_node_to_rc(n) for n in path
                 if _node_map_id(n) == config.ACTIVE_MAP_ID]
            ]
        else:
            local_path = path

        if len(local_path) > 1:
            self._draw_path_overlay(local_path, cell, ox, oy)

        self._draw_path_indices(local_path, cell, ox, oy)

        if self._on_regenerate:
            self._draw_regen_button()

        # Banner + setas de navegação no modo multiverso
        if config.MULTIVERSE_MODE:
            self._draw_map_banner()
            self._draw_nav_arrows(cw, ch)

    # ── layout ───────────────────────────────────────────────────────────────

    def _cell_size(self, cw, ch, grid_rows, grid_cols):
        sx = (cw - 40) // grid_cols
        sy = (ch - 40) // grid_rows
        return max(self._MIN_CELL, min(self._MAX_CELL, sx, sy))

    def _origin(self, cw, ch, cell, grid_rows, grid_cols):
        ox = (cw - cell * grid_cols) // 2
        oy = (ch - cell * grid_rows) // 2
        return ox, oy

    def _tile_rect(self, r, c, cell, ox, oy):
        x1 = ox + c * cell
        y1 = oy + r * cell
        return x1, y1, x1 + cell, y1 + cell

    def _tile_center(self, r, c, cell, ox, oy):
        x1, y1, x2, y2 = self._tile_rect(r, c, cell, ox, oy)
        return (x1 + x2) / 2, (y1 + y2) / 2

    # ── desenho ──────────────────────────────────────────────────────────────

    def _draw_background(self, cw, ch):
        self.create_rectangle(0, 0, cw, ch, fill=COLORS['bg'], outline='')

    def _draw_tile(self, r, c, cell, ox, oy,
                   wall, in_path, is_start, is_goal,
                   is_portal=False,
                   weight=1.0, terrain=None):
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
        elif is_portal:
            fill = COLORS['tile_portal']
            glow = COLORS['tile_portal_glow']
        else:
            glow = None
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
        elif is_portal and cell >= 20:
            # símbolo ⊕ no tile de portal
            f = self._fonts.get('section')
            if f:
                self.create_text(cx, cy, text='⊕', font=f,
                                 fill=COLORS['tile_portal_glow'])
        elif not in_path and cell >= 28:
            self._draw_weight_label(x1, y1, weight)

    def _draw_marker(self, cx, cy, r, color, label):
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=color, outline='')
        f = self._fonts.get('section')
        if f:
            self.create_text(cx, cy, text=label, font=f, fill='#ffffff')

    def _draw_weight_label(self, x1, y1, weight):
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

    def _draw_path_overlay(self, path: list[str], cell, ox, oy):
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

    def _draw_path_indices(self, path: list[str], cell, ox, oy):
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

    def _draw_nav_arrows(self, cw: int, ch: int):
        """
        Setas ◀ / ▶ nas laterais do canvas para navegar entre mapas.
        Desenhadas como retângulos clicáveis com hover — sem widgets Tkinter extras.
        """
        if config.MULTIVERSE is None or not self._on_map_nav:
            return

        mv  = config.MULTIVERSE
        mid = config.ACTIVE_MAP_ID

        aw, ah  = 36, 72          # largura e altura do botão
        margin  = 6               # distância da borda do canvas
        mid_y   = ch // 2
        y1      = mid_y - ah // 2
        y2      = mid_y + ah // 2
        corner  = 6

        f = self._fonts.get('title') or self._fonts.get('section')

        # ── seta esquerda (mapa anterior) ────────────────────────────────────
        if mid > 0:
            lx1, lx2 = margin, margin + aw
            btn_l = self.create_rectangle(
                lx1, y1, lx2, y2,
                fill=COLORS['panel_border'],
                outline=COLORS['accent'], width=1,
                tags='nav_prev',
            )
            self.create_text(
                (lx1 + lx2) / 2, (y1 + y2) / 2,
                text='◀', font=f, fill=COLORS['accent'],
                tags='nav_prev',
            )

            def _prev_enter(_e, b=btn_l):
                self.itemconfig(b, fill=COLORS['node_start'])
                self.config(cursor='hand2')

            def _prev_leave(_e, b=btn_l):
                self.itemconfig(b, fill=COLORS['panel_border'])
                self.config(cursor='')

            self.tag_bind('nav_prev', '<Enter>',    _prev_enter)
            self.tag_bind('nav_prev', '<Leave>',    _prev_leave)
            self.tag_bind('nav_prev', '<Button-1>',
                          lambda _e: self._on_map_nav(-1))

        # ── seta direita (próximo mapa) ───────────────────────────────────────
        if mid < mv.n_maps - 1:
            rx1, rx2 = cw - margin - aw, cw - margin
            btn_r = self.create_rectangle(
                rx1, y1, rx2, y2,
                fill=COLORS['panel_border'],
                outline=COLORS['accent'], width=1,
                tags='nav_next',
            )
            self.create_text(
                (rx1 + rx2) / 2, (y1 + y2) / 2,
                text='▶', font=f, fill=COLORS['accent'],
                tags='nav_next',
            )

            def _next_enter(_e, b=btn_r):
                self.itemconfig(b, fill=COLORS['node_start'])
                self.config(cursor='hand2')

            def _next_leave(_e, b=btn_r):
                self.itemconfig(b, fill=COLORS['panel_border'])
                self.config(cursor='')

            self.tag_bind('nav_next', '<Enter>',    _next_enter)
            self.tag_bind('nav_next', '<Leave>',    _next_leave)
            self.tag_bind('nav_next', '<Button-1>',
                          lambda _e: self._on_map_nav(+1))

    def _draw_map_banner(self):
        """Banner no topo do canvas indicando o mapa ativo."""
        if config.MULTIVERSE is None:
            return
        mv  = config.MULTIVERSE
        mid = config.ACTIVE_MAP_ID
        if mid == mv.start_map:
            label = f'◈  Mapa {mid}  —  INÍCIO'
            color = COLORS['accent']
        elif mid == mv.goal_map:
            label = f'◈  Mapa {mid}  —  SAÍDA REAL'
            color = COLORS['success']
        else:
            label = f'◈  Mapa {mid}'
            color = COLORS['warning']

        f = self._fonts.get('section')
        if f:
            cw = self.winfo_width() or 600
            self.create_text(cw // 2, 14, text=label, font=f,
                             fill=color, anchor='center')