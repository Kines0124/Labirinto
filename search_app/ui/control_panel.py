"""
ui/control_panel.py  —  MERGED (testes-procedural × modificacoes)
==================================================================
Painel esquerdo da interface: seleção de método, estados e botões.

Integração realizada:
  - Checkbox de animação do caminho   (branch testes-procedural)
  - Seção de Multiverso com spinner   (branch modificacoes)
  - Legenda atualizada com portal     (ambas as branches)
  - refresh_states() para atualizar comboboxes após troca de mapa
  - set_pick_active() para destacar botão de pick ativo
"""


from pathlib import Path

from    PIL import Image, ImageTk
import  os
import  tkinter as     tk
from    tkinter import ttk
import  config
from    config  import COLORS, SEARCH_METHODS

HEURISTIC_METHODS = {'Greedy Best-First', 'A* (A-estrela)', 'AIA* (A* Iterativo)'}
HEURISTIC_OPTIONS = ['Manhattan', 'Euclidiana (Multiverso)' ,'Dijkstra (apelação)']


class ControlPanel(tk.Frame):
    """
    Painel de controle lateral esquerdo.

    Callbacks injetados pelo app principal
    ---------------------------------------
    on_search(method, start, goal, depth_limit, heuristic_name) → None
    on_reset()                                                   → None
    on_regenerate()                                              → None
    on_clear_path()                                              → None
    on_clear_result()                                            → None
    on_pick_start()                                              → None
    on_pick_goal()                                               → None
    on_regenerate_multiverse(n_maps, portal_cost)                → None  ← novo
    """

    def __init__(self, parent, on_search, on_reset, fonts: dict,
                 on_regenerate=None, on_clear_path=None, on_clear_result=None,
                 on_pick_start=None, on_pick_goal=None,
                 on_regenerate_multiverse=None,
                 on_exit_multiverse=None, **kwargs):

        super().__init__(parent, bg=COLORS['panel'], width=240,
                         highlightbackground=COLORS['panel_border'],
                         highlightthickness=1, **kwargs)
        self.pack_propagate(False)

        self._on_search                = on_search
        self._on_reset                 = on_reset
        self._fonts                    = fonts
        self._on_regenerate            = on_regenerate
        self._on_clear_path            = on_clear_path
        self._on_clear_result          = on_clear_result
        self._on_pick_start            = on_pick_start
        self._on_pick_goal             = on_pick_goal
        self._on_regenerate_multiverse = on_regenerate_multiverse
        self._on_exit_multiverse       = on_exit_multiverse
        self._pick_btns: dict[str, tk.Button] = {}
        self._legend_imgs = []
        self._build()
        self._apply_combobox_style()

    # ── construção ───────────────────────────────────────────────────────────

    def _build(self):
        pad = {'padx': 16, 'pady': 4}

        # ── método de busca ──────────────────────────────────────────────────
        self._section('▸ MÉTODO DE BUSCA')
        self.method_var = tk.StringVar(value=SEARCH_METHODS[0])
        method_cb = ttk.Combobox(self, textvariable=self.method_var,
                                 values=SEARCH_METHODS, state='readonly',
                                 width=26, font=self._fonts['mono'])
        method_cb.pack(**pad, fill='x')
        method_cb.bind('<<ComboboxSelected>>', self._on_method_change)

        # limite de profundidade
        self._depth_frame = tk.Frame(self, bg=COLORS['panel'])
        self._depth_frame.pack(**pad, fill='x')
        self._depth_label = tk.Label(self._depth_frame,
                                     text='Limite de Profundidade:',
                                     font=self._fonts['section'],
                                     bg=COLORS['panel'],
                                     fg=COLORS['text_dim'])
        self._depth_label.pack(anchor='w')
        self.depth_var = tk.IntVar(value=30)
        tk.Spinbox(self._depth_frame, from_=1, to=50,
                   textvariable=self.depth_var, width=6,
                   command=self._clear,
                   font=self._fonts['mono'],
                   bg=COLORS['node_default'], fg=COLORS['text'],
                   buttonbackground=COLORS['panel_border'],
                   relief='flat', insertbackground=COLORS['text'],
                   ).pack(anchor='w')
        self._depth_frame.pack_forget()

        # heurística
        self._heuristic_frame = tk.Frame(self, bg=COLORS['panel'])
        self._heuristic_frame.pack(**pad, fill='x')
        tk.Label(self._heuristic_frame, text='Heurística:',
                 font=self._fonts['section'], bg=COLORS['panel'],
                 fg=COLORS['text_dim']).pack(anchor='w')
        self.heuristic_var = tk.StringVar(value=HEURISTIC_OPTIONS[0])
        heuristic_cb = ttk.Combobox(self._heuristic_frame,
                                    textvariable=self.heuristic_var,
                                    values=HEURISTIC_OPTIONS,
                                    state='readonly',
                                    width=20, font=self._fonts['mono'])
        heuristic_cb.pack(anchor='w')
        heuristic_cb.bind('<<ComboboxSelected>>', self._clear)
        self._heuristic_frame.pack_forget()

        # ── estado inicial ────────────────────────────────────────────────────
        self._divider()
        self._section('▸ ESTADO INICIAL')
        start_row = tk.Frame(self, bg=COLORS['panel'])
        start_row.pack(padx=16, pady=(0, 4), fill='x')
        self.start_var = tk.StringVar(value=config.STATES[0])
        self.start_var.trace_add('write', self._on_state_change)
        self._start_cb = ttk.Combobox(start_row, textvariable=self.start_var,
                                      values=config.STATES, state='readonly',
                                      width=10, font=self._fonts['mono'])
        self._start_cb.bind('<<ComboboxSelected>>', self._clear)
        self._start_cb.pack(side='left')
        pick_start_btn = tk.Button(
            start_row, text='📍',
            font=self._fonts['mono'],
            bg=COLORS['node_default'], fg=COLORS['accent'],
            activebackground=COLORS['accent'], activeforeground='#ffffff',
            relief='flat', cursor='hand2', padx=6,
            command=self._fire_pick_start)
        pick_start_btn.pack(side='left', padx=(6, 0))
        self._pick_btns['start'] = pick_start_btn

        # ── estado objetivo ───────────────────────────────────────────────────
        self._section('▸ ESTADO OBJETIVO')
        goal_row = tk.Frame(self, bg=COLORS['panel'])
        goal_row.pack(padx=16, pady=(0, 4), fill='x')
        self.goal_var = tk.StringVar(value=config.STATES[-1])
        self.goal_var.trace_add('write', self._on_state_change)
        self._goal_cb = ttk.Combobox(goal_row, textvariable=self.goal_var,
                                     values=config.STATES, state='readonly',
                                     width=10, font=self._fonts['mono'])
        self._goal_cb.bind('<<ComboboxSelected>>', self._clear)
        self._goal_cb.pack(side='left')
        pick_goal_btn = tk.Button(
            goal_row, text='🎯',
            font=self._fonts['mono'],
            bg=COLORS['node_default'], fg=COLORS['success'],
            activebackground=COLORS['success'], activeforeground='#ffffff',
            relief='flat', cursor='hand2', padx=6,
            command=self._fire_pick_goal)
        pick_goal_btn.pack(side='left', padx=(6, 0))
        self._pick_btns['goal'] = pick_goal_btn

        # ── botões de ação ────────────────────────────────────────────────────
        self._divider()

        tk.Button(self, text='▶  EXECUTAR BUSCA',
                  font=self._fonts['section'],
                  bg=COLORS['accent'], fg='#ffffff',
                  activebackground='#6AAAF8', activeforeground='#ffffff',
                  relief='flat', cursor='hand2',
                  command=self._fire_search, pady=8,
                  ).pack(padx=16, pady=(8, 4), fill='x')

        tk.Button(self, text='↺  LIMPAR',
                  font=self._fonts['section'],
                  bg=COLORS['node_default'], fg=COLORS['text_dim'],
                  activebackground=COLORS['panel_border'],
                  activeforeground=COLORS['text'],
                  relief='flat', cursor='hand2',
                  command=self._on_reset, pady=6,
                  ).pack(padx=16, pady=(0, 4), fill='x')

        if self._on_regenerate:
            tk.Button(self, text='⟳  NOVO LABIRINTO',
                      font=self._fonts['section'],
                      bg=COLORS['panel_border'], fg=COLORS['warning'],
                      activebackground=COLORS['node_default'],
                      activeforeground=COLORS['warning'],
                      relief='flat', cursor='hand2',
                      command=self._on_regenerate, pady=6,
                      ).pack(padx=16, pady=(0, 4), fill='x')

        # ── animação ──────────────────────────────────────────────────────────
        self._divider()
        self.animate_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text='Animação do caminho',
                       variable=self.animate_var,
                       font=self._fonts['section'],
                       bg=COLORS['panel'], fg=COLORS['text_dim'],
                       activebackground=COLORS['panel'],
                       selectcolor=COLORS['node_default'],
                       relief='flat', cursor='hand2',
                       ).pack(padx=16, pady=(0, 4), anchor='center')

        # ── seção multiverso ──────────────────────────────────────────────────
        if self._on_regenerate_multiverse:
            self._divider()
            self._section('▸ MULTIVERSO')

            mv_grid = tk.Frame(self, bg=COLORS['panel'])
            mv_grid.pack(padx=16, pady=(0, 4), fill='x')

            tk.Label(mv_grid, text='Nº de mapas:',
                    font=self._fonts['section'],
                    bg=COLORS['panel'], fg=COLORS['text_dim']
                    ).grid(row=0, column=0, sticky='w', pady=2)
            self._n_maps_var = tk.IntVar(value=4)
            tk.Spinbox(mv_grid, from_=2, to=12,
                    textvariable=self._n_maps_var, width=5,
                    font=self._fonts['mono'],
                    bg=COLORS['node_default'], fg=COLORS['text'],
                    buttonbackground=COLORS['panel_border'],
                    relief='flat', insertbackground=COLORS['text'],
                    ).grid(row=0, column=1, sticky='w', padx=(8, 0), pady=2)

            tk.Label(mv_grid, text='Custo do portal:',
                    font=self._fonts['section'],
                    bg=COLORS['panel'], fg=COLORS['text_dim']
                    ).grid(row=1, column=0, sticky='w', pady=2)
            self._portal_cost_var = tk.DoubleVar(value=1.0)
            tk.Spinbox(mv_grid, from_=0.1, to=10.0, increment=0.5,
                    textvariable=self._portal_cost_var, width=5,
                    format='%.1f',
                    font=self._fonts['mono'],
                    bg=COLORS['node_default'], fg=COLORS['text'],
                    buttonbackground=COLORS['panel_border'],
                    relief='flat', insertbackground=COLORS['text'],
                    ).grid(row=1, column=1, sticky='w', padx=(8, 0), pady=2)

            self._gen_mv_btn = tk.Button(self, text='🌀  GERAR MULTIVERSO',
                                    font=self._fonts['section'],
                                    bg=COLORS['accent2'], fg='#ffffff',
                                    activebackground='#C070FF',
                                    activeforeground='#ffffff',
                                    relief='flat', cursor='hand2',
                                    command=self._fire_regenerate_multiverse, pady=6,
                                    )
            self._gen_mv_btn.pack(padx=16, pady=(4, 4), fill='x')
            
            self._exit_mv_btn = tk.Button(
                self, text='✕  SAIR DO MULTIVERSO',
                font=self._fonts['section'],
                bg=COLORS['node_default'], fg=COLORS['warning'],
                activebackground=COLORS['panel_border'],
                activeforeground=COLORS['warning'],
                relief='flat', cursor='hand2',
                command=self._fire_exit_multiverse, pady=6,
            )

            self._divider()
            tk.Button(self, text='◈  LEGENDA / TERRENOS',
                    font=self._fonts['section'],
                    bg=COLORS['panel_border'], fg=COLORS['text_dim'],
                    activebackground=COLORS['node_default'],
                    activeforeground=COLORS['text'],
                    relief='flat', cursor='hand2',
                    command=self._open_legend, pady=6,
                    ).pack(padx=16, pady=(0, 4), fill='x')

    # ── API pública ──────────────────────────────────────────────────────────

    def refresh_states(self, states: list[str],
                       start: str, goal: str):
        """
        Atualiza os comboboxes de início/fim após geração de novo mapa/multiverso.
        Chamado por main.py depois de apply_multiverse() ou regenerate_maze().
        """
        self._start_cb['values'] = states
        self._goal_cb['values']  = states
        self.start_var.set(start)
        self.goal_var.set(goal)

    def set_pick_active(self, role: str | None):
        """Destaca o botão de pick ativo e normaliza o outro."""
        styles = {
            'start': (COLORS['accent'],  '#ffffff'),
            'goal':  (COLORS['success'], '#ffffff'),
        }
        defaults = {
            'start': (COLORS['node_default'], COLORS['accent']),
            'goal':  (COLORS['node_default'], COLORS['success']),
        }
        for key, btn in self._pick_btns.items():
            bg, fg = styles[key] if key == role else defaults[key]
            btn.config(bg=bg, fg=fg)

    # ── eventos ──────────────────────────────────────────────────────────────

    def _fire_pick_start(self):
        self.set_pick_active('start')
        if self._on_pick_start:
            self._on_pick_start()

    def _fire_pick_goal(self):
        self.set_pick_active('goal')
        if self._on_pick_goal:
            self._on_pick_goal()

    def _fire_search(self):
        mapa = {
            'Dijkstra (apelação)':       'dijkstra',
            'Euclidiana (Multiverso)':   'euclidiana',
            'Manhattan':                 'manhattan',
        }
        heuristic_name = mapa.get(self.heuristic_var.get(), 'manhattan')
        self._on_search(
            method=self.method_var.get(),
            start=self.start_var.get(),
            goal=self.goal_var.get(),
            depth_limit=self.depth_var.get(),
            heuristic_name=heuristic_name,
        )

    def _fire_regenerate_multiverse(self):
        if self._on_regenerate_multiverse:
            self._on_regenerate_multiverse(
                n_maps=self._n_maps_var.get(),
                portal_cost=self._portal_cost_var.get(),
            )
            # Revela o botão de saída
            self._exit_mv_btn.pack(padx=16, pady=(0, 4), fill='x',
                       after=self._gen_mv_btn)

    def _fire_regenerate(self):
        """Novo labirinto simples ou multiverso, conforme estado atual."""
        if config.MULTIVERSE_MODE and self._on_regenerate_multiverse:
            self._on_regenerate_multiverse(
                n_maps=self._n_maps_var.get(),
                portal_cost=self._portal_cost_var.get(),
            )
        else:
            if self._on_regenerate:
                self._on_regenerate()

    def _fire_exit_multiverse(self):
        self._exit_mv_btn.pack_forget()
        if self._on_exit_multiverse:
            self._on_exit_multiverse()

    def _on_state_change(self, *_):
        config.START_NODE = self.start_var.get()
        config.GOAL_NODE  = self.goal_var.get()
        self._clear()

    def _on_method_change(self, _event=None):
        self._clear()
        method = self.method_var.get()

        if method == 'Profundidade Limitada':
            self._depth_label.config(text='Limite de Profundidade:')
            self.depth_var.set(30)
            self._depth_frame.pack(padx=16, pady=4, fill='x')
        elif method == 'Aprofundamento Iterativo (IDDFS)':
            self._depth_label.config(text='Profundidade Máxima:')
            self.depth_var.set(30)
            self._depth_frame.pack(padx=16, pady=4, fill='x')
        else:
            self._depth_frame.pack_forget()

        if method in HEURISTIC_METHODS:
            self._heuristic_frame.pack(padx=16, pady=4, fill='x')
        else:
            self._heuristic_frame.pack_forget()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _section(self, text: str):
        tk.Label(self, text=text, font=self._fonts['section'],
                 bg=COLORS['panel'], fg=COLORS['accent2'],
                 anchor='w').pack(padx=16, pady=(10, 2), fill='x')

    def _divider(self):
        tk.Frame(self, bg=COLORS['panel_border'], height=1).pack(
            fill='x', padx=12, pady=6)

    def _clear(self, _event=None):
        if self._on_clear_path:
            self._on_clear_path()
        if self._on_clear_result:
            self._on_clear_result()

    @staticmethod
    def _apply_combobox_style():
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TCombobox',
                        fieldbackground=COLORS['node_default'],
                        background=COLORS['node_default'],
                        foreground=COLORS['text'],
                        selectbackground=COLORS['accent'],
                        selectforeground='#ffffff',
                        arrowcolor=COLORS['accent'],
                        bordercolor=COLORS['panel_border'],
                        lightcolor=COLORS['panel_border'],
                        darkcolor=COLORS['panel_border'])
        style.map('TCombobox',
                  fieldbackground=[('readonly', COLORS['node_default'])],
                  foreground=[('readonly', COLORS['text'])],
                  selectbackground=[('readonly', COLORS['accent'])],
                  selectforeground=[('readonly', '#ffffff')])
        
    def _open_legend(self):
        win = tk.Toplevel(self)
        win.title('Legenda')
        win.configure(bg=COLORS['panel'])
        win.resizable(False, False)

        _ROOT = Path(__file__).parent.parent

        def _load_tileset(filename):
            path =  _ROOT / 'assets' / 'tilesets' / filename
            try:
                img = Image.open(path).resize((32, 32), Image.NEAREST)
                tk_img = ImageTk.PhotoImage(img)
                self._legend_imgs.append(tk_img)
                return tk_img
            except Exception:
                return None

        def _section(text):
            tk.Label(win, text=text, font=self._fonts['section'],
                    bg=COLORS['panel'], fg=COLORS['accent2'],
                    anchor='w').pack(padx=16, pady=(10, 2), fill='x')

        def _divider():
            tk.Frame(win, bg=COLORS['panel_border'], height=1).pack(
                fill='x', padx=12, pady=6)

        _section('▸ ESTADOS E TRANSIÇÕES')
        for filename, label in [
            ('start.png',  'Estado inicial'),
            ('goal.png',   'Estado objetivo'),
            ('path.png',   'Caminho encontrado'),
            ('portal.png', 'Portal de mapa'),
        ]:
            row = tk.Frame(win, bg=COLORS['panel'])
            row.pack(anchor='w', padx=16, pady=2)

            tk_img = _load_tileset(filename)
            if tk_img:
                tk.Label(row, image=tk_img,
                        bg=COLORS['panel']).pack(side='left')
            else:
                tk.Label(row, text='●', font=self._fonts['label'],
                        fg=COLORS['text_dim'], bg=COLORS['panel']).pack(side='left')

            tk.Label(row, text=label, font=self._fonts['label'],
                    fg=COLORS['text_dim'], bg=COLORS['panel'],
                    ).pack(side='left', padx=8)

        _divider()
        _section('▸ TERRENOS')
        for filename, label in [
            ('plains.png',   'Planície  (peso 1)'),
            ('forest.png',   'Floresta  (peso 2)'),
            ('swamp.png',    'Pântano   (peso 3)'),
            ('mountain.png', 'Montanha  (peso 5)'),
            ('wall.png',     'Parede    (bloqueio)'),
        ]:
            row = tk.Frame(win, bg=COLORS['panel'])
            row.pack(anchor='w', padx=16, pady=2)

            tk_img = _load_tileset(filename)
            if tk_img:
                tk.Label(row, image=tk_img,
                        bg=COLORS['panel']).pack(side='left')
            else:
                # Fallback: quadrado colorido se imagem não carregar
                tk.Label(row, text='■', font=self._fonts['label'],
                        fg=COLORS['text_dim'], bg=COLORS['panel']).pack(side='left')

            tk.Label(row, text=label, font=self._fonts['label'],
                    fg=COLORS['text_dim'], bg=COLORS['panel'],
                    ).pack(side='left', padx=8)

        _divider()
        tk.Button(win, text='Fechar',
                font=self._fonts['section'],
                bg=COLORS['node_default'], fg=COLORS['text_dim'],
                activebackground=COLORS['panel_border'],
                relief='flat', cursor='hand2',
                command=win.destroy, pady=6,
                ).pack(padx=16, pady=(0, 12), fill='x')
        
        win.withdraw()
        win.update_idletasks()
        root = self.winfo_toplevel()
        w = win.winfo_reqwidth() + 80
        h = win.winfo_reqheight()
        x = root.winfo_rootx() + (root.winfo_width()  - w) // 2
        y = root.winfo_rooty() + (root.winfo_height() - h) // 2
        win.geometry(f'{w}x{h}+{x}+{y}')
        win.deiconify()
