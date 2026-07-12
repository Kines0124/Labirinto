"""
ui/control_panel.py 
==================================================================
Left panel of the interface: method selection, states, and buttons.
"""


from pathlib import Path

from    PIL import Image, ImageTk
import  os
import  tkinter as     tk
from    tkinter import ttk
import  config
from    config  import COLORS, SEARCH_METHODS
from    i18n    import (t, method_label, method_canonical,
                        heuristic_label, heuristic_canonical)

# Canonical (language-independent) keys — these are what get passed to
# run_search / on_search. Display text is derived via i18n.heuristic_label()
# and translated back with i18n.heuristic_canonical(); see i18n.py.
HEURISTIC_METHODS = {'Greedy Best-First', 'A* (A-estrela)', 'AIA* (A* Iterativo)'}
HEURISTIC_IDS_NORMAL     = ['manhattan', 'dijkstra']
HEURISTIC_IDS_MULTIVERSE = ['euclidiana', 'dijkstra']


class ControlPanel(tk.Frame):
    """Left-side control panel."""

    def __init__(self, parent, on_search, on_reset, fonts: dict,
                 on_regenerate=None, on_clear_path=None, on_clear_result=None,
                 on_pick_start=None, on_pick_goal=None,
                 on_regenerate_multiverse=None,
                 on_exit_multiverse=None, **kwargs):
        """Initializes the panel, registers callbacks, and builds the widgets."""

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
        self._section_lbls: list[tk.Label]   = []   # (widget, key) pairs for refresh_texts
        self._build()
        self._apply_combobox_style()

    # ── build ────────────────────────────────────────────────────────────────

    def _build(self):
        """Builds all panel widgets: method, states, buttons, and multiverse."""
        pad = {'padx': 16, 'pady': 4}

        # ── search method ────────────────────────────────────────────────────
        self._method_section_lbl = self._section('search_method_section')
        self.method_var = tk.StringVar(value=method_label(SEARCH_METHODS[0]))
        self._method_cb = ttk.Combobox(self, textvariable=self.method_var,
                                 values=[method_label(m) for m in SEARCH_METHODS],
                                 state='readonly',
                                 width=26, font=self._fonts['mono'])
        self._method_cb.pack(**pad, fill='x')
        self._method_cb.bind('<<ComboboxSelected>>', self._on_method_change)

        # depth limit
        self._depth_frame = tk.Frame(self, bg=COLORS['panel'])
        self._depth_frame.pack(**pad, fill='x')
        self._depth_label = tk.Label(self._depth_frame,
                                     text=t('depth_limit_label'),
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

        # heuristic
        self._heuristic_frame = tk.Frame(self, bg=COLORS['panel'])
        self._heuristic_frame.pack(**pad, fill='x')
        self._heuristic_lbl = tk.Label(self._heuristic_frame, text=t('heuristic_label'),
                 font=self._fonts['section'], bg=COLORS['panel'],
                 fg=COLORS['text_dim'])
        self._heuristic_lbl.pack(anchor='w')
        self.heuristic_var = tk.StringVar(value=heuristic_label(HEURISTIC_IDS_NORMAL[0]))
        self._heuristic_cb = ttk.Combobox(self._heuristic_frame,
                                    textvariable=self.heuristic_var,
                                    values=[heuristic_label(h) for h in HEURISTIC_IDS_NORMAL],
                                    state='readonly',
                                    width=20, font=self._fonts['mono'])
        self._heuristic_cb.pack(anchor='w')
        self._heuristic_cb.bind('<<ComboboxSelected>>', self._clear)
        self._heuristic_frame.pack_forget()

        # ── start state ──────────────────────────────────────────────────────
        self._divider()
        self._start_section_lbl = self._section('start_state_section')
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

        # ── goal state ───────────────────────────────────────────────────────
        self._goal_section_lbl = self._section('goal_state_section')
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

        # ── action buttons ───────────────────────────────────────────────────
        self._divider()

        self._run_btn = tk.Button(self, text=t('run_search_btn'),
                  font=self._fonts['section'],
                  bg=COLORS['accent'], fg='#ffffff',
                  activebackground='#6AAAF8', activeforeground='#ffffff',
                  relief='flat', cursor='hand2',
                  command=self._fire_search, pady=8,
                  )
        self._run_btn.pack(padx=16, pady=(8, 4), fill='x')

        self._clear_btn = tk.Button(self, text=t('clear_btn'),
                  font=self._fonts['section'],
                  bg=COLORS['node_default'], fg=COLORS['text_dim'],
                  activebackground=COLORS['panel_border'],
                  activeforeground=COLORS['text'],
                  relief='flat', cursor='hand2',
                  command=self._on_reset, pady=6,
                  )
        self._clear_btn.pack(padx=16, pady=(0, 4), fill='x')

        self._new_maze_btn = None
        if self._on_regenerate:
            self._new_maze_btn = tk.Button(self, text=t('new_maze_btn'),
                      font=self._fonts['section'],
                      bg=COLORS['panel_border'], fg=COLORS['warning'],
                      activebackground=COLORS['node_default'],
                      activeforeground=COLORS['warning'],
                      relief='flat', cursor='hand2',
                      command=self._on_regenerate, pady=6,
                      )
            self._new_maze_btn.pack(padx=16, pady=(0, 4), fill='x')

        # ── animation ────────────────────────────────────────────────────────
        self._divider()
        self.animate_var = tk.BooleanVar(value=True)
        self._animate_chk = tk.Checkbutton(self, text=t('path_animation_label'),
                       variable=self.animate_var,
                       font=self._fonts['section'],
                       bg=COLORS['panel'], fg=COLORS['text_dim'],
                       activebackground=COLORS['panel'],
                       selectcolor=COLORS['node_default'],
                       relief='flat', cursor='hand2',
                       )
        self._animate_chk.pack(padx=16, pady=(0, 4), anchor='center')

        # ── multiverse section ──────────────────────────────────────────────
        self._mv_section_lbl = None
        if self._on_regenerate_multiverse:
            self._divider()
            self._mv_section_lbl = self._section('multiverse_section')

            mv_grid = tk.Frame(self, bg=COLORS['panel'])
            mv_grid.pack(padx=16, pady=(0, 4), fill='x')

            self._num_maps_lbl = tk.Label(mv_grid, text=t('num_maps_label'),
                    font=self._fonts['section'],
                    bg=COLORS['panel'], fg=COLORS['text_dim']
                    )
            self._num_maps_lbl.grid(row=0, column=0, sticky='w', pady=2)
            self._n_maps_var = tk.IntVar(value=4)
            tk.Spinbox(mv_grid, from_=2, to=12,
                    textvariable=self._n_maps_var, width=5,
                    font=self._fonts['mono'],
                    bg=COLORS['node_default'], fg=COLORS['text'],
                    buttonbackground=COLORS['panel_border'],
                    relief='flat', insertbackground=COLORS['text'],
                    ).grid(row=0, column=1, sticky='w', padx=(8, 0), pady=2)

            self._portal_cost_lbl = tk.Label(mv_grid, text=t('portal_cost_label'),
                    font=self._fonts['section'],
                    bg=COLORS['panel'], fg=COLORS['text_dim']
                    )
            self._portal_cost_lbl.grid(row=1, column=0, sticky='w', pady=2)
            self._portal_cost_var = tk.DoubleVar(value=1.0)
            tk.Spinbox(mv_grid, from_=0.1, to=10.0, increment=0.5,
                    textvariable=self._portal_cost_var, width=5,
                    format='%.1f',
                    font=self._fonts['mono'],
                    bg=COLORS['node_default'], fg=COLORS['text'],
                    buttonbackground=COLORS['panel_border'],
                    relief='flat', insertbackground=COLORS['text'],
                    ).grid(row=1, column=1, sticky='w', padx=(8, 0), pady=2)

            self._gen_mv_btn = tk.Button(self, text=t('generate_multiverse_btn'),
                                    font=self._fonts['section'],
                                    bg=COLORS['accent2'], fg='#ffffff',
                                    activebackground="#FAAB50",
                                    activeforeground='#ffffff',
                                    relief='flat', cursor='hand2',
                                    command=self._fire_regenerate_multiverse, pady=6,
                                    )
            self._gen_mv_btn.pack(padx=16, pady=(4, 4), fill='x')
            
            self._exit_mv_btn = tk.Button(
                self, text=t('exit_multiverse_btn'),
                font=self._fonts['section'],
                bg=COLORS['node_default'], fg=COLORS['warning'],
                activebackground=COLORS['panel_border'],
                activeforeground=COLORS['warning'],
                relief='flat', cursor='hand2',
                command=self._fire_exit_multiverse, pady=6,
            )

            self._divider()
            self._legend_btn = tk.Button(self, text=t('legend_btn'),
                    font=self._fonts['section'],
                    bg=COLORS['panel_border'], fg=COLORS['text_dim'],
                    activebackground=COLORS['node_default'],
                    activeforeground=COLORS['text'],
                    relief='flat', cursor='hand2',
                    command=self._open_legend, pady=6,
                    )
            self._legend_btn.pack(padx=16, pady=(0, 4), fill='x')

    # ── public API ───────────────────────────────────────────────────────────

    def refresh_states(self, states: list[str],
                       start: str, goal: str):
        """Updates the start/goal comboboxes after a new map is generated."""
        self._start_cb['values'] = states
        self._goal_cb['values']  = states
        self.start_var.set(start)
        self.goal_var.set(goal)

    def set_pick_active(self, role: str | None):
        """Highlights the active pick button and resets the other one."""
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

    def refresh_texts(self):
        """Re-applies translated strings to every widget after a language
        change, preserving the current selections (method, heuristic,
        start/goal are untouched — only their displayed labels update)."""
        self._method_section_lbl.config(text=t('search_method_section'))
        self._start_section_lbl.config(text=t('start_state_section'))
        self._goal_section_lbl.config(text=t('goal_state_section'))
        self._depth_label.config(
            text=t('max_depth_label')
            if method_canonical(self.method_var.get()) == 'Aprofundamento Iterativo (IDDFS)'
            else t('depth_limit_label'))
        self._heuristic_lbl.config(text=t('heuristic_label'))
        self._run_btn.config(text=t('run_search_btn'))
        self._clear_btn.config(text=t('clear_btn'))
        if self._new_maze_btn:
            self._new_maze_btn.config(text=t('new_maze_btn'))
        self._animate_chk.config(text=t('path_animation_label'))

        # method combobox: keep the same canonical selection, translate display
        current_method_canonical = method_canonical(self.method_var.get())
        self._method_cb['values'] = [method_label(m) for m in SEARCH_METHODS]
        self.method_var.set(method_label(current_method_canonical))

        # heuristic combobox: keep the same canonical selection, translate display
        current_heuristic_canonical = heuristic_canonical(self.heuristic_var.get())
        ids = HEURISTIC_IDS_MULTIVERSE if config.MULTIVERSE_MODE else HEURISTIC_IDS_NORMAL
        self._heuristic_cb['values'] = [heuristic_label(h) for h in ids]
        self.heuristic_var.set(heuristic_label(current_heuristic_canonical))

        if self._mv_section_lbl:
            self._mv_section_lbl.config(text=t('multiverse_section'))
            self._num_maps_lbl.config(text=t('num_maps_label'))
            self._portal_cost_lbl.config(text=t('portal_cost_label'))
            self._gen_mv_btn.config(text=t('generate_multiverse_btn'))
            self._exit_mv_btn.config(text=t('exit_multiverse_btn'))
            self._legend_btn.config(text=t('legend_btn'))

    # ── events ───────────────────────────────────────────────────────────────

    def _fire_pick_start(self):
        """Activates start-node pick mode and notifies the app."""
        self.set_pick_active('start')
        if self._on_pick_start:
            self._on_pick_start()

    def _fire_pick_goal(self):
        """Activates goal-node pick mode and notifies the app."""
        self.set_pick_active('goal')
        if self._on_pick_goal:
            self._on_pick_goal()

    def _fire_search(self):
        """Reads the fields and fires the search callback with the current
        parameters. Display labels are translated back to their canonical
        (language-independent) values before being passed on, since
        run_search dispatches on the canonical strings."""
        heuristic_name = heuristic_canonical(self.heuristic_var.get())
        self._on_search(
            method=method_canonical(self.method_var.get()),
            start=self.start_var.get(),
            goal=self.goal_var.get(),
            depth_limit=self.depth_var.get(),
            heuristic_name=heuristic_name,
        )

    def refresh_heuristics(self):
        """Filters the heuristic options according to the active multiverse mode."""
        ids = HEURISTIC_IDS_MULTIVERSE if config.MULTIVERSE_MODE else HEURISTIC_IDS_NORMAL
        options = [heuristic_label(h) for h in ids]

        self._heuristic_cb['values'] = options

        if self.heuristic_var.get() not in options:
            self.heuristic_var.set(options[0])

    def _fire_regenerate_multiverse(self):
        """Fires multiverse generation and reveals the exit button."""
        if self._on_regenerate_multiverse:
            self._on_regenerate_multiverse(
                n_maps=self._n_maps_var.get(),
                portal_cost=self._portal_cost_var.get(),
            )
            # Reveals the exit button
            self._exit_mv_btn.pack(padx=16, pady=(0, 4), fill='x',
                       after=self._gen_mv_btn)
            self.refresh_heuristics() 

    def _fire_regenerate(self):
        """New simple maze or multiverse, depending on the current state."""
        if config.MULTIVERSE_MODE and self._on_regenerate_multiverse:
            self._on_regenerate_multiverse(
                n_maps=self._n_maps_var.get(),
                portal_cost=self._portal_cost_var.get(),
            )
        else:
            if self._on_regenerate:
                self._on_regenerate()

    def _fire_exit_multiverse(self):
        """Hides the exit button and notifies the app to leave multiverse mode."""
        self._exit_mv_btn.pack_forget()
        if self._on_exit_multiverse:
            self._on_exit_multiverse()
        self.refresh_heuristics()

    def _on_state_change(self, *_):
        """Updates start/goal in config and clears the result when the comboboxes change."""
        config.START_NODE = self.start_var.get()
        config.GOAL_NODE  = self.goal_var.get()
        self._clear()

    def _on_method_change(self, _event=None):
        """Shows or hides the depth/heuristic frames depending on the method."""
        self._clear()
        method = method_canonical(self.method_var.get())

        if method == 'Profundidade Limitada':
            self._depth_label.config(text=t('depth_limit_label'))
            self.depth_var.set(30)
            self._depth_frame.pack(padx=16, pady=4, fill='x')
        elif method == 'Aprofundamento Iterativo (IDDFS)':
            self._depth_label.config(text=t('max_depth_label'))
            self.depth_var.set(30)
            self._depth_frame.pack(padx=16, pady=4, fill='x')
        else:
            self._depth_frame.pack_forget()

        if method in HEURISTIC_METHODS:
            self._heuristic_frame.pack(padx=16, pady=4, fill='x')
        else:
            self._heuristic_frame.pack_forget()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _section(self, key: str) -> tk.Label:
        """Renders a section label with header styling. *key* is an i18n key;
        returns the widget so refresh_texts() can update it later."""
        lbl = tk.Label(self, text=t(key), font=self._fonts['section'],
                 bg=COLORS['panel'], fg=COLORS['accent2'],
                 anchor='w')
        lbl.pack(padx=16, pady=(10, 2), fill='x')
        return lbl

    def _divider(self):
        """Inserts a horizontal divider line between sections."""
        tk.Frame(self, bg=COLORS['panel_border'], height=1).pack(
            fill='x', padx=12, pady=6)

    def _clear(self, _event=None):
        """Clears the path and result displayed on the canvas."""
        if self._on_clear_path:
            self._on_clear_path()
        if self._on_clear_result:
            self._on_clear_result()

    @staticmethod
    def _apply_combobox_style():
        """Applies the app's custom visual theme to ttk Combobox widgets."""
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
        """Opens the legend window with terrain and state tiles."""
        win = tk.Toplevel(self)
        win.title(t('legend_title'))
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

        _section(t('states_transitions_section'))
        for filename, label_key in [
            ('start.png',  'start_state_item'),
            ('goal.png',   'goal_state_item'),
            ('path.png',   'path_found_item'),
            ('portal.png', 'map_portal_item'),
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

            tk.Label(row, text=t(label_key), font=self._fonts['label'],
                    fg=COLORS['text_dim'], bg=COLORS['panel'],
                    ).pack(side='left', padx=8)

        _divider()
        _section(t('terrains_section'))
        for filename, label_key in [
            ('plains.png',   'terrain_plains'),
            ('forest.png',   'terrain_forest'),
            ('swamp.png',    'terrain_swamp'),
            ('mountain.png', 'terrain_mountain'),
            ('wall.png',     'terrain_wall'),
        ]:
            row = tk.Frame(win, bg=COLORS['panel'])
            row.pack(anchor='w', padx=16, pady=2)

            tk_img = _load_tileset(filename)
            if tk_img:
                tk.Label(row, image=tk_img,
                        bg=COLORS['panel']).pack(side='left')
            else:
                # Fallback: colored square if the image fails to load
                tk.Label(row, text='■', font=self._fonts['label'],
                        fg=COLORS['text_dim'], bg=COLORS['panel']).pack(side='left')

            tk.Label(row, text=t(label_key), font=self._fonts['label'],
                    fg=COLORS['text_dim'], bg=COLORS['panel'],
                    ).pack(side='left', padx=8)

        _divider()
        tk.Button(win, text=t('close'),
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