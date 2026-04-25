"""
ui/graph_canvas.py  —  MERGED (testes-procedural × modificacoes)
=================================================================
Widget de canvas responsável pela renderização do mapa em grid.

Integração realizada:
  - Tilesets PNG e sprites animados  (branch testes-procedural)
  - Suporte completo ao modo multiverso: portais, banner e setas de
    navegação entre mapas               (branch modificacoes)
  - Transição de mapa instantânea: ao mudar de mapa todos os jobs de
    animação pendentes são cancelados antes do re-render, evitando
    conflitos de estado no Tkinter.
  - Rastro do percurso preservado entre mapas (path não é limpo na
    troca de mapa ativo).
"""

from __future__ import annotations
from pathlib import Path
import tkinter as tk
import config
from config import COLORS
from PIL import Image, ImageTk  # pip install pillow


# ─────────────────────────────────────────────────────────────────────────────
# Utilitários de nó
# ─────────────────────────────────────────────────────────────────────────────

def _node_to_rc(node: str) -> tuple[int, int]:
    """
    Converte um nó para (row, col).
    Aceita tanto "(r,c)"  quanto  "M2:(r,c)".
    """
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


# Mapeamento terreno → chave de tileset
_TERRAIN_TILE: dict[str, str] = {
    'plains':   'plains',
    'forest':   'forest',
    'swamp':    'swamp',
    'mountain': 'mountain',
}

# Mapeamento terreno → chave de cor de fallback (quando tileset ausente)
_TERRAIN_COLOR: dict[str, str] = {
    'plains':   'tile_free',
    'forest':   'tile_w2',
    'swamp':    'tile_w3',
    'mountain': 'tile_w5',
}


# ─────────────────────────────────────────────────────────────────────────────
# Widget principal
# ─────────────────────────────────────────────────────────────────────────────

class GraphCanvas(tk.Canvas):
    """
    Canvas que renderiza o mapa como um grid de tiles.

    Modo simples     →  render(path, start, goal)  com nós "(r,c)"
    Modo multiverso  →  mesmo método; filtra nós do mapa ativo e exibe
                        banner + setas de navegação.

    Todos os jobs de animação são cancelados antes de qualquer re-render,
    garantindo que a troca de mapa não deixe sprites "fantasmas".
    """

    _MIN_CELL = 20
    _MAX_CELL = 48

    def __init__(self, parent, on_regenerate=None, on_node_picked=None,
                 on_map_nav=None, animation_on=True, **kwargs):
        super().__init__(parent, bg=COLORS['bg'],
                         highlightthickness=0, **kwargs)

        self._fonts: dict = {}
        self._on_regenerate  = on_regenerate
        self._on_node_picked = on_node_picked
        self._on_map_nav     = on_map_nav       # callback(delta: int)
        self._animation_on   = animation_on
        self._pick_mode: str | None = None

        # cache de imagens PIL/Tk
        self._tile_imgs:  dict[str, ImageTk.PhotoImage] = {}
        self._tile_pil:   dict[str, Image.Image]        = {}
        self._temp_imgs:  list[ImageTk.PhotoImage]      = []

        # sprites animados
        self._sprite_frames:    dict[str, list[ImageTk.PhotoImage]] = {}
        self._sprite_frame_idx: dict[str, int]                      = {}
        self._anim_jobs:        dict[str, str]                       = {}

        self._cached_cell: int | None = None

        self.bind('<Configure>', lambda _e: self._reload_tiles() or self.render())
        self.bind('<Button-1>',  self._on_canvas_click)

    # ── API pública ──────────────────────────────────────────────────────────

    def set_fonts(self, fonts: dict):
        self._fonts = fonts

    def set_animate(self, value: bool):
        self._animation_on = value

    def clear_path(self):
        self.render(path=[])

    def set_pick_mode(self, mode: str | None):
        self._pick_mode = mode
        self.config(cursor='crosshair' if mode else '')

    # ── carregamento de assets ───────────────────────────────────────────────

    def _reload_tiles(self):
        """Redimensiona os tilesets para o cell size atual e cacheia."""
        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480
        cell = self._cell_size(cw, ch, config.GRID_ROWS, config.GRID_COLS)

        if self._cached_cell == cell:
            return
        self._cached_cell = cell

        _ROOT = Path(__file__).parent.parent

        tile_paths = {
            'plains':   _ROOT / 'assets' / 'tilesets' / 'plains.png',
            'forest':   _ROOT / 'assets' / 'tilesets' / 'forest.png',
            'swamp':    _ROOT / 'assets' / 'tilesets' / 'swamp.png',
            'mountain': _ROOT / 'assets' / 'tilesets' / 'mountain.png',
            'wall':     _ROOT / 'assets' / 'tilesets' / 'wall.png',
            'path':     _ROOT / 'assets' / 'tilesets' / 'path.png',
        }
        self._tile_imgs = {}
        self._tile_pil  = {}
        for name, filepath in tile_paths.items():
            try:
                img = Image.open(filepath).convert('RGBA').resize(
                    (cell, cell), Image.NEAREST)
                self._tile_pil[name]  = img
                self._tile_imgs[name] = ImageTk.PhotoImage(img)
            except Exception:
                pass  # sem asset → fallback por cor

        self._sprite_frames    = {}
        self._sprite_frame_idx = {}

        for sheet in ('start_down', 'start_up', 'start_left', 'start_right', 'goal'):
            frames = self._load_spritesheet(
                _ROOT / 'assets' / 'tilesets' / f'{sheet}_sheet.png', cell)
            self._sprite_frames[sheet]    = frames
            self._sprite_frame_idx[sheet] = 0

        end_frames = self._load_spritesheet(
            _ROOT / 'assets' / 'tilesets' / 'end_sheet.png', cell)
        self._sprite_frames['end']    = end_frames
        self._sprite_frame_idx['end'] = 0

    def _load_spritesheet(self, path: Path, cell: int,
                          frame_size: int = 32) -> list[ImageTk.PhotoImage]:
        try:
            sheet    = Image.open(path).convert('RGBA')
            n_frames = sheet.width // frame_size
            method   = Image.LANCZOS if cell <= 32 else Image.NEAREST
            frames   = []
            for i in range(n_frames):
                frame = sheet.crop(
                    (i * frame_size, 0, (i + 1) * frame_size, frame_size))
                frame = frame.resize((cell, cell), method)
                base  = Image.new('RGBA', (cell, cell), (0, 0, 0, 0))
                base.alpha_composite(frame)
                frames.append(ImageTk.PhotoImage(base))
            return frames
        except Exception:
            return []

    # ── clique para selecionar nó ────────────────────────────────────────────

    def _on_canvas_click(self, event):
        if not self._pick_mode:
            return

        grid_map  = config.GRID_MAP
        grid_rows = config.GRID_ROWS
        grid_cols = config.GRID_COLS

        cw   = self.winfo_width()  or 600
        ch   = self.winfo_height() or 480
        cell = self._cell_size(cw, ch, grid_rows, grid_cols)
        ox, oy = self._origin(cw, ch, cell, grid_rows, grid_cols)

        c = (event.x - ox) // cell
        r = (event.y - oy) // cell

        if not (0 <= r < grid_rows and 0 <= c < grid_cols):
            return
        if grid_map[r][c] == 1:
            return

        if config.MULTIVERSE_MODE:
            node = f"M{config.ACTIVE_MAP_ID}:({r},{c})"
        else:
            node = f"({r},{c})"

        role = self._pick_mode
        self.set_pick_mode(None)
        if self._on_node_picked:
            self._on_node_picked(role, node)

    # ── cancelamento seguro de animações ─────────────────────────────────────

    def _cancel_all_anim(self):
        """Cancela todos os after-jobs pendentes antes de qualquer re-render."""
        for job_id in list(self._anim_jobs.values()):
            try:
                self.after_cancel(job_id)
            except Exception:
                pass
        self._anim_jobs = {}

    # ── render principal ─────────────────────────────────────────────────────

    def render(self, path: list[str] = None,
               start: str = None, goal: str = None):
        """
        Redesenha o mapa completo lendo os globais atuais de config.

        No modo multiverso filtra o caminho para exibir apenas os nós
        do mapa ativo — mas NÃO descarta path, preservando o rastro
        completo para análise posterior e para re-render ao navegar mapas.
        """
        self._cancel_all_anim()
        self.delete('all')

        grid_map     = config.GRID_MAP
        grid_weights = config.GRID_WEIGHTS
        grid_rows    = config.GRID_ROWS
        grid_cols    = config.GRID_COLS
        terrain_map  = config.TERRAIN_MAP

        path  = path  if path  is not None else []
        start = start or config.START_NODE
        goal  = goal  or config.GOAL_NODE

        # Filtra caminho para o mapa ativo (multiverso)
        if config.MULTIVERSE_MODE:
            active_id  = config.ACTIVE_MAP_ID
            local_path = [n for n in path if _node_map_id(n) == active_id]
            path_set   = {_node_to_rc(n) for n in local_path}
            start_rc   = (_node_to_rc(start)
                          if _node_map_id(start) == active_id else None)
            goal_rc    = (_node_to_rc(goal)
                          if _node_map_id(goal)  == active_id else None)
        else:
            local_path = path
            path_set   = {_node_to_rc(n) for n in path}
            start_rc   = _node_to_rc(start) if start else None
            goal_rc    = _node_to_rc(goal)  if goal  else None

        # Células de portal no mapa ativo
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
        self._temp_imgs = []

        # Tiles base (path desenhado depois, pela animação)
        for r in range(grid_rows):
            for c in range(grid_cols):
                rc      = (r, c)
                wall    = grid_map[r][c] == 1
                weight  = grid_weights[r][c] or 1.0
                terrain = (terrain_map[r][c]
                            if terrain_map and not wall else None)

                # índice do nó no caminho local (para rotação do tile de path)
                if config.MULTIVERSE_MODE:
                    lnode = f"M{config.ACTIVE_MAP_ID}:({r},{c})"
                else:
                    lnode = f"({r},{c})"
                idx = local_path.index(lnode) if lnode in local_path else -1

                self._draw_tile(
                    r, c, cell, ox, oy,
                    wall=wall,
                    in_path=False,
                    is_start=(start_rc == rc),
                    is_goal =(goal_rc  == rc),
                    is_portal=(rc in portal_cells and not wall),
                    weight=weight,
                    terrain=terrain,
                    idx=idx,
                    path=local_path,
                )

        # Animação ou desenho estático do caminho
        if self._animation_on and local_path:
            self._animate_path(local_path, cell, ox, oy, start, goal, index=0)
        else:
            if local_path:
                for idx, node in enumerate(local_path):
                    r, c = _node_to_rc(node)
                    self._draw_tile(
                        r, c, cell, ox, oy,
                        wall=False, in_path=True,
                        is_start=(start_rc == (r, c)),
                        is_goal =(goal_rc  == (r, c)),
                        is_portal=False,
                        weight=1,
                        terrain=(terrain_map[r][c] if terrain_map else None),
                        idx=idx, path=local_path,
                    )
                self._draw_path_overlay(local_path, cell, ox, oy)
                self._draw_path_indices(local_path, cell, ox, oy)

            # relança ticks de idle para start/goal
            for name in ('start', 'goal'):
                sheet = 'start_down' if name == 'start' else 'goal'
                if self._sprite_frames.get(sheet):
                    job = self.after(120, lambda n=name: self._tick_sprite(n))
                    self._anim_jobs[name] = job

        if self._on_regenerate:
            self._draw_regen_button()

        if config.MULTIVERSE_MODE:
            self._draw_map_banner()
            self._draw_nav_arrows(cw, ch)

    # ── animação de caminho ──────────────────────────────────────────────────

    def _animate_path(self, path, cell, ox, oy, start, goal, index=0):
        if not path or index >= len(path):
            self.delete('sprite_start')
            self.delete('sprite_goal')
            for name in ('start', 'goal'):
                self._anim_jobs.pop(name, None)
            if path:
                gr, gc = _node_to_rc(path[-1])
                self._play_end_animation(gr, gc, cell, ox, oy, frame_idx=0)
            return

        node = path[index]
        r, c = _node_to_rc(node)

        if index > 0:
            pr, pc = _node_to_rc(path[index - 1])
            self._draw_tile(
                pr, pc, cell, ox, oy,
                wall=False, in_path=True,
                is_start=False, is_goal=False, is_portal=False,
                weight=1,
                terrain=(config.TERRAIN_MAP[pr][pc]
                         if config.TERRAIN_MAP else None),
                idx=index - 1, path=path,
            )
            self.delete('sprite_start')

        x1, y1     = ox + c * cell, oy + r * cell
        sheet_name = self._start_direction(index, path)
        n_frames   = len(self._sprite_frames.get(sheet_name, [1]))
        self._sprite_frame_idx[sheet_name] = (
            self._sprite_frame_idx.get(sheet_name, 0) + 1
        ) % max(n_frames, 1)
        frames = self._sprite_frames.get(sheet_name, [])
        if frames:
            self.delete('sprite_start')
            self.create_image(x1, y1, anchor='nw',
                              image=frames[self._sprite_frame_idx[sheet_name]],
                              tags='sprite_start')

        job = self.after(100, lambda: self._animate_path(
            path, cell, ox, oy, start, goal, index + 1))
        self._anim_jobs['path_walk'] = job

    def _play_end_animation(self, r, c, cell, ox, oy, frame_idx=0):
        frames = self._sprite_frames.get('end', [])
        if not frames:
            return
        x1, y1 = ox + c * cell, oy + r * cell
        self.delete('sprite_end')
        self.create_image(x1, y1, anchor='nw',
                          image=frames[frame_idx], tags='sprite_end')
        next_idx = (frame_idx + 1) % len(frames)
        job = self.after(120, lambda: self._play_end_animation(
            r, c, cell, ox, oy, next_idx))
        self._anim_jobs['end'] = job

    def _tick_sprite(self, name: str):
        sheet_name = 'start_down' if name == 'start' else name
        frames = self._sprite_frames.get(sheet_name, [])
        if not frames:
            return
        self._sprite_frame_idx[sheet_name] = (
            self._sprite_frame_idx.get(sheet_name, 0) + 1
        ) % len(frames)

        node = config.START_NODE if name == 'start' else config.GOAL_NODE
        # No modo multiverso: só anima se o nó pertence ao mapa ativo
        if config.MULTIVERSE_MODE and _node_map_id(node) != config.ACTIVE_MAP_ID:
            return

        r, c = _node_to_rc(node)
        cw   = self.winfo_width()  or 600
        ch   = self.winfo_height() or 480
        cell = self._cell_size(cw, ch, config.GRID_ROWS, config.GRID_COLS)
        ox, oy = self._origin(cw, ch, cell, config.GRID_ROWS, config.GRID_COLS)
        x1, y1 = ox + c * cell, oy + r * cell

        tag = f'sprite_{name}'
        self.delete(tag)
        self.create_image(x1, y1, anchor='nw',
                          image=frames[self._sprite_frame_idx[sheet_name]],
                          tags=tag)
        job = self.after(120, lambda n=name: self._tick_sprite(n))
        self._anim_jobs[name] = job

    # ── direção do sprite ────────────────────────────────────────────────────

    def _start_direction(self, idx: int, path: list[str]) -> str:
        def delta(a, b):
            ra, ca = _node_to_rc(a)
            rb, cb = _node_to_rc(b)
            return rb - ra, cb - ca

        dr, dc = delta(path[idx], path[idx + 1]) \
            if idx < len(path) - 1 else delta(path[idx - 1], path[idx])
        return {
            (1,  0): 'start_down',
            (-1, 0): 'start_up',
            (0, -1): 'start_left',
            (0,  1): 'start_right',
        }.get((dr, dc), 'start_down')

    def _path_rotation(self, idx: int, path: list[str]) -> float:
        def delta(a, b):
            ra, ca = _node_to_rc(a)
            rb, cb = _node_to_rc(b)
            return rb - ra, cb - ca

        dr, dc = delta(path[idx], path[idx + 1]) \
            if idx < len(path) - 1 else delta(path[idx - 1], path[idx])
        return {(1, 0): 0, (-1, 0): 180, (0, 1): 90, (0, -1): 270}.get((dr, dc), 0)

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

    # ── desenho de tiles ─────────────────────────────────────────────────────

    def _draw_background(self, cw, ch):
        self.create_rectangle(0, 0, cw, ch, fill=COLORS['bg'], outline='')

    def _draw_tile(self, r, c, cell, ox, oy,
                   wall, in_path, is_start, is_goal,
                   is_portal=False,
                   weight=1.0, terrain=None,
                   idx=-1, path=None):
        x1, y1, x2, y2 = self._tile_rect(r, c, cell, ox, oy)

        # tile base (imagem PNG ou fallback por cor)
        if wall:
            base_key = 'wall'
        elif terrain is not None:
            base_key = _TERRAIN_TILE.get(terrain.name, 'plains')
        else:
            base_key = 'plains'

        base_img = self._tile_imgs.get(base_key)
        if base_img:
            self.create_image(x1, y1, anchor='nw', image=base_img)
        else:
            self._draw_tile_color_fallback(
                x1, y1, x2, y2, wall, in_path,
                is_start, is_goal, is_portal, weight, terrain)

        # sobreposição do tile de path
        if in_path and not is_start and not is_goal and not wall:
            angle   = self._path_rotation(idx, path) if path and idx >= 0 else 0
            pil_img = self._tile_pil.get('path')
            if pil_img:
                rotated = pil_img.rotate(angle, expand=False)
                tk_img  = ImageTk.PhotoImage(rotated)
                self._temp_imgs.append(tk_img)
                self.create_image(x1, y1, anchor='nw', image=tk_img)

        # portal: overlay translúcido + símbolo (sem asset específico)
        if is_portal and not wall and not is_start and not is_goal:
            self.create_rectangle(
                x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                fill=COLORS['tile_portal'],
                outline=COLORS['tile_portal_glow'], width=2,
                stipple='gray50')
            if cell >= 20:
                f = self._fonts.get('section')
                if f:
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    self.create_text(cx, cy, text='⊕', font=f,
                                     fill=COLORS['tile_portal_glow'])

        # sprites de start e goal
        for role, color, label in (
            ('start', COLORS['accent'],  'S'),
            ('goal',  COLORS['success'], 'G'),
        ):
            if (role == 'start' and is_start) or (role == 'goal' and is_goal):
                sheet_name = 'start_down' if role == 'start' else 'goal'
                frames = self._sprite_frames.get(sheet_name, [])
                if frames:
                    tag = f'sprite_{role}'
                    self.delete(tag)
                    self.create_image(
                        x1, y1, anchor='nw',
                        image=frames[self._sprite_frame_idx.get(sheet_name, 0)],
                        tags=tag)
                else:
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    self._draw_marker(cx, cy, max(4, cell // 5), color, label)
                break

    def _draw_tile_color_fallback(self, x1, y1, x2, y2,
                                  wall, in_path, is_start, is_goal,
                                  is_portal, weight, terrain):
        """Renderização por cores quando assets PNG não estão disponíveis."""
        pad = 1
        if wall:
            self.create_rectangle(
                x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                fill=COLORS['tile_wall'],
                outline=COLORS['tile_border'], width=1)
            self.create_line(x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                             fill=COLORS['tile_border'], width=1)
            self.create_line(x2 - pad, y1 + pad, x1 + pad, y2 - pad,
                             fill=COLORS['tile_border'], width=1)
            return

        if is_start:
            fill, glow = COLORS['node_start'], COLORS['node_glow_start']
        elif is_goal:
            fill, glow = COLORS['node_goal'],  COLORS['node_glow_goal']
        elif in_path:
            fill, glow = COLORS['node_path'],  COLORS['node_glow_path']
        elif is_portal:
            fill, glow = COLORS['tile_portal'], COLORS['tile_portal_glow']
        else:
            glow = None
            if terrain is not None:
                fill = COLORS[_TERRAIN_COLOR.get(terrain.name, 'tile_free')]
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
            width=1 if not glow else 2)

    def _draw_marker(self, cx, cy, r, color, label):
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=color, outline='')
        f = self._fonts.get('section')
        if f:
            self.create_text(cx, cy, text=label, font=f, fill='#ffffff')

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

    # ── botão flutuante ───────────────────────────────────────────────────────

    def _draw_regen_button(self):
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
            tags='regen_btn')
        self.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text='⟳  Novo Labirinto',
            font=self._fonts.get('section'),
            fill='#ffffff',
            tags='regen_btn')

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

    # ── UI de multiverso: banner e setas ─────────────────────────────────────

    def _draw_map_banner(self):
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

        f  = self._fonts.get('section')
        cw = self.winfo_width() or 600
        if f:
            self.create_text(cw // 2, 14, text=label, font=f,
                             fill=color, anchor='center')

    def _draw_nav_arrows(self, cw: int, ch: int):
        """
        Setas ◀ / ▶ nas laterais para navegar entre mapas.
        Ao clicar, chama on_map_nav(±1), que em main.py atualiza
        config e chama render() com o caminho completo já calculado.
        """
        if config.MULTIVERSE is None or not self._on_map_nav:
            return

        mv  = config.MULTIVERSE
        mid = config.ACTIVE_MAP_ID
        aw, ah = 36, 72
        margin = 6
        mid_y  = ch // 2
        y1, y2 = mid_y - ah // 2, mid_y + ah // 2
        f = self._fonts.get('title') or self._fonts.get('section')

        if mid > 0:
            lx1, lx2 = margin, margin + aw
            btn_l = self.create_rectangle(
                lx1, y1, lx2, y2,
                fill=COLORS['panel_border'],
                outline=COLORS['accent'], width=1,
                tags='nav_prev')
            self.create_text((lx1 + lx2) / 2, (y1 + y2) / 2,
                             text='◀', font=f, fill=COLORS['accent'],
                             tags='nav_prev')

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

        if mid < mv.n_maps - 1:
            rx1, rx2 = cw - margin - aw, cw - margin
            btn_r = self.create_rectangle(
                rx1, y1, rx2, y2,
                fill=COLORS['panel_border'],
                outline=COLORS['accent'], width=1,
                tags='nav_next')
            self.create_text((rx1 + rx2) / 2, (y1 + y2) / 2,
                             text='▶', font=f, fill=COLORS['accent'],
                             tags='nav_next')

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