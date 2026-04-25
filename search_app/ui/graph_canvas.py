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

    def __init__(self, parent, on_regenerate=None, on_node_picked=None, animation_on=True, **kwargs):
        super().__init__(parent, bg=COLORS['bg'],
                         highlightthickness=0, **kwargs)
        self._fonts: dict = {}
        self._on_regenerate = on_regenerate
        self._on_node_picked = on_node_picked   # callback(role, node)
        self._animation_on = animation_on
        self._pick_mode: str | None = None       # 'start' | 'goal' | None
        # self.bind('<Configure>', lambda _e: self.render())                # USAR ISSO PRA INTERFACE DEFAULT
        self.bind('<Button-1>', self._on_canvas_click)
        # USAR AS DUAS LINHAS ABAIXO PARA INTERFACE COM TILESETS
        self._tile_imgs: dict[str, ImageTk.PhotoImage] = {}  
        self.bind('<Configure>', lambda _e: self._reload_tiles() or self.render())  # ← troca
        
    def clear_path(self):
        self.render(path=[])

    def set_animate(self, value: bool):
        self._animation_on = value

    def set_pick_mode(self, mode: str | None):
        """Ativa ('start'/'goal') ou desativa (None) o modo de seleção por clique."""
        self._pick_mode = mode
        if mode == 'start':
            self.config(cursor='crosshair')
        elif mode == 'goal':
            self.config(cursor='crosshair')
        else:
            self.config(cursor='')

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
        if grid_map[r][c] == 1:          # parede — ignora
            return

        node = f"({r},{c})"
        role = self._pick_mode
        self.set_pick_mode(None)         # desativa após a seleção

        if self._on_node_picked:
            self._on_node_picked(role, node)

    def set_fonts(self, fonts: dict):
        self._fonts = fonts

    def _path_rotation(self, idx: int, path: list[str]) -> float:
        """Retorna o ângulo de rotação em graus para o tile na posição idx."""
        def delta(a, b):
            ra, ca = _node_to_rc(a)
            rb, cb = _node_to_rc(b)
            return rb - ra, cb - ca  # (dr, dc)

        # usa o segmento anterior ou posterior dependendo da posição
        if idx < len(path) - 1:
            dr, dc = delta(path[idx], path[idx + 1])
        else:
            dr, dc = delta(path[idx - 1], path[idx])

        # dr=+1 → desce (sul), dr=-1 → sobe (norte)
        # dc=+1 → direita (leste), dc=-1 → esquerda (oeste)
        angle_map = {
            (1,  0): 0,    # sul   → não altera
            (-1, 0): 180,  # norte → 180°
            (0, 1): 90,   # oeste → 90° direita
            (0, -1): 270,  # leste → 90° esquerda
        }
        return angle_map.get((dr, dc), 0)
    
    def _start_direction(self, idx: int, path: list[str]) -> str:
        def delta(a, b):
            ra, ca = _node_to_rc(a)
            rb, cb = _node_to_rc(b)
            return rb - ra, cb - ca

        if idx < len(path) - 1:
            dr, dc = delta(path[idx], path[idx + 1])
        else:
            dr, dc = delta(path[idx - 1], path[idx])

        direction_map = {
            (1,  0): 'start_down',
            (-1, 0): 'start_up',
            (0, -1): 'start_left',
            (0,  1): 'start_right',
        }
        return direction_map.get((dr, dc), 'start_down')

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

        paths ={
            'plains':   _ROOT / 'assets' / 'tilesets' / 'plains.png',
            'forest':   _ROOT / 'assets' / 'tilesets' / 'forest.png',
            'swamp':    _ROOT / 'assets' / 'tilesets' / 'swamp.png',
            'mountain': _ROOT / 'assets' / 'tilesets' / 'mountain.png',
            'wall':     _ROOT / 'assets' / 'tilesets' / 'wall.png',
            'path':     _ROOT / 'assets' / 'tilesets' / 'path.png', 
            # 'start':    _ROOT / 'assets' / 'tilesets' / 'start.png',
            # 'goal':     _ROOT / 'assets' / 'tilesets' / 'goal.png',
        }
        self._tile_imgs = {}
        self._tile_pil: dict[str, Image.Image] = {}   
        for name, filepath in paths.items():
            img = Image.open(filepath).convert('RGBA').resize((cell, cell), Image.NEAREST) # Trocar pra Image.LANCZOS para alta resolução
            self._tile_pil[name] = img
            self._tile_imgs[name] = ImageTk.PhotoImage(img)

        # FRAMES START E GOAL ANIMADOS
        self._sprite_frames: dict[str, list[ImageTk.PhotoImage]] = {}
        self._sprite_frame_idx: dict[str, int] = {}

        for name in ('start_down', 'start_up', 'start_left', 'start_right', 'goal'):
            frames = self._load_spritesheet(
                _ROOT / 'assets' / 'tilesets' / f'{name}_sheet.png',
                cell
            )
            self._sprite_frames[name] = frames
            self._sprite_frame_idx[name] = 0

        self._sprite_frames['end'] = self._load_spritesheet(
        _ROOT / 'assets' / 'tilesets' / 'end_sheet.png', cell
        )

    def _load_spritesheet(self, path: Path, cell: int,
                        frame_size: int = 32) -> list[ImageTk.PhotoImage]:
        sheet = Image.open(path).convert('RGBA')
        n_frames = sheet.width // frame_size
        method = Image.LANCZOS if cell <= 32 else Image.NEAREST
        frames = []
        for i in range(n_frames):
            frame = sheet.crop((i * frame_size, 0, (i + 1) * frame_size, frame_size))
            frame = frame.resize((cell, cell), method)

            # compõe sobre fundo transparente para preservar alpha
            base = Image.new('RGBA', (cell, cell), (0, 0, 0, 0))
            base.alpha_composite(frame)
            frames.append(ImageTk.PhotoImage(base))
        return frames

    def _tick_sprite(self, name: str):
        # para start, usa start_down como idle
        sheet_name = 'start_down' if name == 'start' else name
        frames = self._sprite_frames.get(sheet_name, [])
        if not frames:
            return
        self._sprite_frame_idx[sheet_name] = (
            self._sprite_frame_idx.get(sheet_name, 0) + 1
        ) % len(frames)

        node = config.START_NODE if name == 'start' else config.GOAL_NODE
        r, c = _node_to_rc(node)

        cw = self.winfo_width()  or 600
        ch = self.winfo_height() or 480
        cell = self._cell_size(cw, ch, config.GRID_ROWS, config.GRID_COLS)
        ox, oy = self._origin(cw, ch, cell, config.GRID_ROWS, config.GRID_COLS)

        x1 = ox + c * cell
        y1 = oy + r * cell

        tag = f'sprite_{name}'
        self.delete(tag)
        self.create_image(x1, y1, anchor='nw',
                        image=frames[self._sprite_frame_idx[sheet_name]],
                        tags=tag)

        job = self.after(120, lambda n=name: self._tick_sprite(n))
        self._anim_jobs[name] = job

    def _animate_path(self, path, cell, ox, oy, start, goal, index=0):
        if not path or index >= len(path):
            self._draw_path_indices(path, cell, ox, oy)

            self.delete('sprite_start')
            self.delete('sprite_goal')

            for name in ('start', 'goal'):
                if name in self._anim_jobs:
                    self.after_cancel(self._anim_jobs.pop(name))

            if path:  # ← só toca end se ainda há path válido
                goal_node = path[-1]
                gr, gc = _node_to_rc(goal_node)
                self._play_end_animation(gr, gc, cell, ox, oy, frame_idx=0)
            return
        
        node = path[index]
        r, c = _node_to_rc(node)

        # desenha o path.png nos tiles já percorridos
        if index > 0:
            past_node = path[index - 1]
            pr, pc = _node_to_rc(past_node)
            self._draw_tile(
                pr, pc, cell, ox, oy,
                wall=False, in_path=True,
                is_start=False, is_goal=False,
                weight=1,
                terrain=config.TERRAIN_MAP[pr][pc] if config.TERRAIN_MAP else None,
                idx=index - 1, path=path,
            )

        # apaga o sprite do start da posição anterior
        if index > 0:
            self.delete('sprite_start')

       # desenha o start na posição atual com sheet direcional
        x1 = ox + c * cell
        y1 = oy + r * cell
        sheet_name = self._start_direction(index, path)
        self._sprite_frame_idx[sheet_name] = (
            self._sprite_frame_idx.get(sheet_name, 0) + 1
        ) % len(self._sprite_frames[sheet_name])
        frames = self._sprite_frames.get(sheet_name, [])
        if frames:
            tag = 'sprite_start'
            self.delete(tag)
            self.create_image(x1, y1, anchor='nw',
                            image=frames[self._sprite_frame_idx[sheet_name]],
                            tags=tag)
        delay = 100  # ms entre cada tile
        job = self.after(delay, lambda: self._animate_path(
            path, cell, ox, oy, start, goal, index + 1
        ))
        self._anim_jobs['path_walk'] = job

    def _play_end_animation(self, r, c, cell, ox, oy, frame_idx=0):
        frames = self._sprite_frames.get('end', [])
        if not frames:
            return
        x1 = ox + c * cell
        y1 = oy + r * cell
        self.delete('sprite_end')
        self.create_image(x1, y1, anchor='nw', image=frames[frame_idx], tags='sprite_end')
        next_idx = (frame_idx + 1) % len(frames)
        self._anim_jobs['end'] = self.after(120, lambda: self._play_end_animation(
            r, c, cell, ox, oy, next_idx
        ))
    # ── API pública ──────────────────────────────────────────────────────────

    def render(self, path=None, start=None, goal=None):
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
        self._temp_imgs = []

        if not hasattr(self, '_anim_jobs'):
            self._anim_jobs = {}

        # cancela ticks anteriores
        for job in self._anim_jobs.values():
            self.after_cancel(job)
        self._anim_jobs = {}

        for r in range(grid_rows):
            for c in range(grid_cols):
                node    = f"({r},{c})"
                wall    = grid_map[r][c] == 1
                weight  = grid_weights[r][c] or 1.0
                terrain = (terrain_map[r][c] if terrain_map and not wall else None)
                idx     = path.index(node) if node in path_set else -1
                self._draw_tile(
                    r, c, cell, ox, oy,
                    wall=wall,
                    in_path=False,        # ← sem path por enquanto
                    is_start=(node == start),
                    is_goal=(node == goal),
                    weight=weight,
                    terrain=terrain,
                    idx=idx,
                    path=path,
                )

        if self._animation_on and path:
            self._animate_path(path, cell, ox, oy, start, goal, index=0)
        else:
            if path:
                for idx, node in enumerate(path):
                    r, c = _node_to_rc(node)
                    self._draw_tile(
                        r, c, cell, ox, oy,
                        wall=False, in_path=True,
                        is_start=(node == start), is_goal=(node == goal),
                        weight=1,
                        terrain=config.TERRAIN_MAP[r][c] if config.TERRAIN_MAP else None,
                        idx=idx, path=path,
                    )
                self._draw_path_indices(path, cell, ox, oy)

            # sempre religa os ticks de start e goal, com ou sem path
            for name in ('start', 'goal'):
                sheet = 'start_down' if name == 'start' else 'goal'
                if self._sprite_frames.get(sheet):
                    self._anim_jobs[name] = self.after(120, lambda n=name: self._tick_sprite(n))
        # CAMINHO TRAÇADO
        # if len(path) > 1:
        #     self._draw_path_overlay(path, cell, ox, oy)

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

    # DESCOMENTAR ISSO AQUI E DELETAR O _draw_tile ANTERIOR

    def _draw_tile(self, r, c, cell, ox, oy, wall, in_path,
                is_start, is_goal, weight, terrain=None, idx=-1, path=None):
        x1, y1, x2, y2 = self._tile_rect(r, c, cell, ox, oy)

        # TILE BASE
        if wall:
            base_key = 'wall'
        elif terrain is not None:
            base_key = terrain.name
        else:
            base_key = 'plains'

        # DESCOMENTAR PARA CONTORNO EM TORNO DO TILE DO CAMINHO 
        # if in_path and not is_start and not is_goal and not wall:
        #     pad = max(2, cell // 8)
        #     self.create_rectangle(
        #         x1 - pad, y1 - pad, x2 + pad, y2 + pad,
        #         fill=COLORS.get('edge_glow', '#ffe066'),
        #         outline='',
        #     )

        base_img = self._tile_imgs.get(base_key)
        if base_img:
            self.create_image(x1, y1, anchor='nw', image=base_img)

        # SOBREPOSIÇÃO DO PATH POR CIMA DO TILE
        if in_path and not is_start and not is_goal and not wall:
            angle = self._path_rotation(idx, path)  
            pil_img = self._tile_pil.get('path')
            if pil_img:
                rotated = pil_img.rotate(angle, expand=False)  
                tk_img = ImageTk.PhotoImage(rotated)
                self._temp_imgs.append(tk_img)  
                self.create_image(x1, y1, anchor='nw', image=tk_img)

        # START E GOAL
        for role, color, label in (
            ('start', COLORS['accent'],  'S'),
            ('goal',  COLORS['success'], 'G'),
        ):
            if (role == 'start' and is_start) or (role == 'goal' and is_goal):
                sheet_name = 'start_down' if role == 'start' else 'goal'  # ← aqui
                frames = self._sprite_frames.get(sheet_name, [])
                if frames:
                    tag = f'sprite_{role}'
                    self.delete(tag)
                    self.create_image(x1, y1, anchor='nw',
                                    image=frames[self._sprite_frame_idx.get(sheet_name, 0)],
                                    tags=tag)
                else:
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    self._draw_marker(cx, cy, max(4, cell // 5), color, label)
                break

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