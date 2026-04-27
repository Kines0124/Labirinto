"""
main.py  —  v3 (travessia automática de portais + rastro fixo)
==============================================================
Orquestrador principal da aplicação.

Novidades
---------
- on_map_switch  →  chamado pelo GraphCanvas quando o personagem cruza
                    um portal durante a animação. Atualiza config para
                    o novo mapa SEM cancelar animação nem chamar render().
- _handle_map_nav →  navegação manual pelas setas usa render(static=True):
                     exibe o caminho já traçado como rastro fixo, sem
                     reanimar. O sprite fica em idle na última posição
                     visitada naquele mapa.
"""
import webbrowser
import tkinter as tk
from tkinter import font

import config
from config import COLORS, WINDOW
from algorithms import run_search
from multiverse import generate_multiverse
from ui.graph_canvas import GraphCanvas
from ui.control_panel import ControlPanel
from ui.result_panel import ResultPanel


class SearchApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(WINDOW['title'])
        self.configure(bg=COLORS['bg'])
        self.resizable(True, True)
        self.minsize(WINDOW['min_width'], WINDOW['min_height'])

        self._fonts = self._create_fonts()
        self._last_path:  list[str] = []
        self._last_start: str = config.START_NODE
        self._last_goal:  str = config.GOAL_NODE
        self._build_ui()
        self._center_window()

    # ── fontes ────────────────────────────────────────────────────────────────

    def _create_fonts(self) -> dict:
        return {
            'title':   font.Font(family='Courier', size=13, weight='bold'),
            'label':   font.Font(family='Courier', size=9),
            'section': font.Font(family='Courier', size=8,  weight='bold'),
            'mono':    font.Font(family='Courier', size=9),
            'big':     font.Font(family='Courier', size=22, weight='bold'),
            'node':    font.Font(family='Courier', size=11, weight='bold'),
        }

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()

        body = tk.Frame(self, bg=COLORS['bg'])
        body.pack(fill='both', expand=True)

        self.control = ControlPanel(
            body,
            on_search=self._handle_search,
            on_reset=self._handle_reset,
            on_regenerate=self._handle_regenerate,
            on_clear_path=lambda: self.graph_canvas.clear_path(),
            on_clear_result=lambda: self.result.clear(),
            on_pick_start=lambda: self.graph_canvas.set_pick_mode('start'),
            on_pick_goal=lambda: self.graph_canvas.set_pick_mode('goal'),
            on_regenerate_multiverse=self._handle_regenerate_multiverse,
            fonts=self._fonts,
        )
        self.control.pack(side='left', fill='y', padx=(8, 4), pady=8)

        canvas_wrapper = tk.Frame(body, bg=COLORS['bg'])
        canvas_wrapper.pack(side='left', fill='both', expand=True, padx=4, pady=8)
        tk.Label(canvas_wrapper, text='LABIRINTO GERADO',
                 font=self._fonts['section'],
                 bg=COLORS['bg'], fg=COLORS['text_dim'],
                 anchor='w').pack(padx=4, pady=(4, 0))

        self.graph_canvas = GraphCanvas(
            canvas_wrapper,
            on_regenerate=self._handle_regenerate,
            on_node_picked=self._handle_node_picked,
            on_map_nav=self._handle_map_nav,
            on_map_switch=self._handle_map_switch,   # ← novo
            animation_on=True,
        )
        self.graph_canvas.set_fonts(self._fonts)
        self.graph_canvas.pack(fill='both', expand=True)

        self.control.animate_var.trace_add(
            'write', lambda *_: self.graph_canvas.set_animate(
                self.control.animate_var.get()))

        self.result = ResultPanel(body, fonts=self._fonts)
        self.result.pack(side='right', fill='y', padx=(4, 8), pady=8)

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS['panel'], height=48)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        tk.Label(header, text='◈  LABIRINTO  ◈',
                 font=self._fonts['title'],
                 bg=COLORS['panel'], fg=COLORS['accent'],
                 ).pack(side='left', padx=20, pady=10)

        btn_style = dict(font=self._fonts['label'], relief='flat',
                         cursor='hand2', padx=14, pady=4)

        tk.Button(header, text='✕  Sair',
                  bg=COLORS['panel'], fg=COLORS['text_dim'],
                  activebackground='#c0392b', activeforeground='#ffffff',
                  command=self.destroy, **btn_style,
                  ).pack(side='right', padx=(4, 16), pady=8)

        tk.Button(header, text='ℹ  Sobre',
                  bg=COLORS['panel'], fg=COLORS['text_dim'],
                  activebackground=COLORS['accent'], activeforeground='#ffffff',
                  command=self._show_about, **btn_style,
                  ).pack(side='right', padx=4, pady=8)

    def _center_window(self):
        self.update_idletasks()
        w, h = WINDOW['width'], WINDOW['height']
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    # ── callbacks ─────────────────────────────────────────────────────────────

    def _handle_search(self, method: str, start: str,
                       goal: str, depth_limit: int,
                       heuristic_name: str = 'manhattan'):
        if start == goal:
            self.result.set_status('⚠ Estado inicial = objetivo.',
                                   COLORS['warning'])
            return

        self.result.set_status(f'Executando {method}...', COLORS['accent'])
        self.update()

        graph = config.SUPER_GRAPH if config.MULTIVERSE_MODE else config.GRAPH
        effective_heuristic = ('dijkstra' if config.MULTIVERSE_MODE
                               else heuristic_name)

        result = run_search(
            method=method,
            start=start,
            goal=goal,
            graph=graph,
            heuristic=None,
            depth_limit=depth_limit,
            heuristic_name=effective_heuristic,
        )

        # Limpa histórico de visitas antes de iniciar nova animação
        self.graph_canvas.reset_visited()

        self.graph_canvas.render(path=result.path, start=start, goal=goal)
        self.result.update_result(result)

        self._last_path  = result.path
        self._last_start = start
        self._last_goal  = goal

        if result.found:
            self.result.set_status(
                f'✓ Caminho encontrado! {len(result.path)} nós.',
                COLORS['success'])
        else:
            self.result.set_status('✗ Sem caminho encontrado.',
                                   COLORS['danger'])

    def _handle_regenerate(self):
        config.regenerate_maze()
        config.MULTIVERSE_MODE = False
        self.graph_canvas.reset_visited()
        self.control.refresh_states(
            config.STATES, config.START_NODE, config.GOAL_NODE)
        self.graph_canvas.render()
        self.result.clear()

    def _handle_regenerate_multiverse(self, n_maps: int, portal_cost: float):
        self.result.set_status('Gerando multiverso...', COLORS['accent'])
        self.update()

        mv = generate_multiverse(
            n_maps=n_maps,
            rows=config.MAZE_LOGICAL_ROWS,
            cols=config.MAZE_LOGICAL_COLS,
            portal_cost=portal_cost,
        )
        config.apply_multiverse(mv)

        self._last_path  = []
        self._last_start = config.START_NODE
        self._last_goal  = config.GOAL_NODE
        self.graph_canvas.reset_visited()

        self.control.refresh_states(
            [config.START_NODE, config.GOAL_NODE],
            config.START_NODE,
            config.GOAL_NODE,
        )
        self.graph_canvas.render()
        self.result.clear()
        self.result.set_status(
            f'✓ Multiverso gerado: {n_maps} mapas, '
            f'{len(mv.portals)//2} portais.',
            COLORS['success'],
        )

    def _handle_map_switch(self, new_map_id: int):
        """
        Chamado pelo GraphCanvas durante a animação ao cruzar um portal.
        Atualiza config para o novo mapa SEM interromper a animação.
        O GraphCanvas já redesenhou os tiles; aqui só atualizamos o estado.
        """
        if not config.MULTIVERSE_MODE or config.MULTIVERSE is None:
            return
        if 0 <= new_map_id < config.MULTIVERSE.n_maps:
            config._apply_active_map(new_map_id)

    def _handle_map_nav(self, delta: int):
        """
        Navegação manual pelas setas ◀ / ▶.
        Usa render(static=True): mostra o rastro já traçado como tiles
        fixos sem reanimar. O sprite aparece em idle na última posição
        visitada naquele mapa.
        """
        if not config.MULTIVERSE_MODE or config.MULTIVERSE is None:
            return
        new_id = config.ACTIVE_MAP_ID + delta
        if 0 <= new_id < config.MULTIVERSE.n_maps:
            config._apply_active_map(new_id)
            self.graph_canvas.render(
                path=self._last_path,
                start=self._last_start,
                goal=self._last_goal,
                static=True,            # ← rastro fixo, sem reanimar
            )

    def _handle_reset(self):
        start = self.control.start_var.get()
        goal  = self.control.goal_var.get()
        self.graph_canvas.render(start=start, goal=goal)
        self.result.clear()

    def _handle_node_picked(self, role: str, node: str):
        self.control.set_pick_active(None)
        if role == 'start':
            self.control.start_var.set(node)
            config.START_NODE = node
        else:
            self.control.goal_var.set(node)
            config.GOAL_NODE = node
        self.graph_canvas.clear_path()
        self.result.clear()
        start = self.control.start_var.get()
        goal  = self.control.goal_var.get()
        self.graph_canvas.render(start=start, goal=goal)

    # ── Sobre ─────────────────────────────────────────────────────────────────

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title('Sobre')
        win.resizable(False, False)
        win.configure(bg=COLORS['panel'])
        win.grab_set()

        w, h = 630, 480
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        win.geometry(f'{w}x{h}+{x}+{y}')

        font_family = self._fonts['label'].actual()['family']
        base_size   = self._fonts['label'].actual()['size']

        main_frame = tk.Frame(win, bg=COLORS['panel'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)

        tk.Label(main_frame, text='◈  Sobre  ◈',
                 font=self._fonts['title'],
                 bg=COLORS['panel'], fg=COLORS['accent']
                 ).pack(pady=(10, 15))

        tk.Label(main_frame, text='DESENVOLVIDO POR',
                 font=(font_family, base_size, 'bold'),
                 bg=COLORS['panel'], fg=COLORS['accent']).pack()

        tk.Label(main_frame,
                 text='Guilherme Carvalho Alvarenga & Lara Hydalgo Ferreira',
                 font=(self._fonts['label'], base_size + 2, 'bold'),
                 bg=COLORS['panel'], fg=COLORS['text']).pack(pady=(0, 20))

        desc_text = (
            'Visualizador interativo de algoritmos de busca em inteligência artificial. '
            'O labirinto é gerado proceduralmente e percorrido por estratégias de busca '
            'para comparação de custo e profundidade em tempo real.'
        )
        tk.Label(main_frame, text=desc_text,
                 font=self._fonts['label'],
                 bg=COLORS['panel'], fg=COLORS['text'],
                 justify='left', wraplength=550
                 ).pack(pady=10)

        tk.Label(main_frame, text='\n\nPara mais informações acesse o repositório: ',
                 font=(font_family, base_size + 2, 'bold'),
                 bg=COLORS['panel'], fg=COLORS['accent']
                 ).pack(pady=(15, 0))

        repo_url = 'https://github.com/Kines0124/Labirinto'
        link_label = tk.Label(main_frame, text=repo_url,
                              font=(font_family, base_size, 'underline'),
                              bg=COLORS['panel'], fg='#58a6ff',
                              cursor='hand2')
        link_label.pack(pady=15)
        link_label.bind('<Button-1>', lambda e: webbrowser.open_new(repo_url))

        tk.Button(main_frame, text='Fechar',
                  font=self._fonts['label'],
                  bg=COLORS['accent'], fg='#ffffff',
                  activebackground=COLORS['node_glow_start'],
                  relief='flat', cursor='hand2',
                  padx=30, pady=8,
                  command=win.destroy
                  ).pack(side='bottom', pady=20)


if __name__ == '__main__':
    app = SearchApp()
    app.mainloop()