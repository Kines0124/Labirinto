"""
ui/control_panel.py
===================
Painel esquerdo da interface: seleção de método, estados e botões de ação.
Não conhece algoritmos nem canvas — comunica-se com o app via callbacks.
"""

import tkinter as tk
from tkinter import ttk
from config import COLORS, STATES, SEARCH_METHODS


class ControlPanel(tk.Frame):
    """
    Painel de controle lateral esquerdo.

    Callbacks injetados pelo app principal
    ---------------------------------------
    on_search(method, start, goal, depth_limit) → None
    on_reset()                                  → None
    """

    def __init__(self, parent, on_search, on_reset, fonts: dict, **kwargs):
        super().__init__(parent, bg=COLORS['panel'], width=230,
                         highlightbackground=COLORS['panel_border'],
                         highlightthickness=1, **kwargs)
        self.pack_propagate(False)

        self._on_search = on_search
        self._on_reset  = on_reset
        self._fonts     = fonts

        self._build()
        self._apply_combobox_style()

    # ── construção ──────────────────────────────────────────────────────────

    def _build(self):
        pad = {'padx': 16, 'pady': 4}

        # ── método de busca ──
        self._section('▸ MÉTODO DE BUSCA')
        self.method_var = tk.StringVar(value=SEARCH_METHODS[0])
        method_cb = ttk.Combobox(self, textvariable=self.method_var,
                                 values=SEARCH_METHODS, state='readonly',
                                 width=26, font=self._fonts['mono'])
        method_cb.pack(**pad, fill='x')
        method_cb.bind('<<ComboboxSelected>>', self._on_method_change)

        # ── limite de profundidade (visível só para DLS) ──
        self._depth_frame = tk.Frame(self, bg=COLORS['panel'])
        self._depth_frame.pack(**pad, fill='x')
        tk.Label(self._depth_frame, text='Limite de Profundidade:',
                 font=self._fonts['section'], bg=COLORS['panel'],
                 fg=COLORS['text_dim']).pack(anchor='w')
        self.depth_var = tk.IntVar(value=3)
        tk.Spinbox(self._depth_frame, from_=1, to=20,
                   textvariable=self.depth_var, width=6,
                   font=self._fonts['mono'],
                   bg=COLORS['node_default'], fg=COLORS['text'],
                   buttonbackground=COLORS['panel_border'],
                   relief='flat', insertbackground=COLORS['text'],
                   ).pack(anchor='w')
        self._depth_frame.pack_forget()

        # ── estado inicial ──
        self._divider()
        self._section('▸ ESTADO INICIAL')
        self.start_var = tk.StringVar(value=STATES[0])
        ttk.Combobox(self, textvariable=self.start_var,
                     values=STATES, state='readonly',
                     width=10, font=self._fonts['mono'],
                     ).pack(**pad, anchor='w')

        # ── estado objetivo ──
        self._section('▸ ESTADO OBJETIVO')
        self.goal_var = tk.StringVar(value=STATES[-1])
        ttk.Combobox(self, textvariable=self.goal_var,
                     values=STATES, state='readonly',
                     width=10, font=self._fonts['mono'],
                     ).pack(**pad, anchor='w')

        # ── botões ──
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

        # ── legenda ──
        self._divider()
        self._section('▸ LEGENDA')
        for clr, label in [
            (COLORS['accent'],   'Estado inicial'),
            (COLORS['success'],  'Estado objetivo'),
            (COLORS['accent2'],  'Caminho encontrado'),
            (COLORS['text_dim'], 'Estado não visitado'),
        ]:
            row = tk.Frame(self, bg=COLORS['panel'])
            row.pack(anchor='w', padx=16, pady=1)
            tk.Label(row, text='●', font=self._fonts['label'],
                     fg=clr, bg=COLORS['panel']).pack(side='left')
            tk.Label(row, text=label, font=self._fonts['label'],
                     fg=COLORS['text_dim'], bg=COLORS['panel'],
                     ).pack(side='left', padx=4)

    # ── eventos ─────────────────────────────────────────────────────────────

    def _fire_search(self):
        self._on_search(
            method=self.method_var.get(),
            start=self.start_var.get(),
            goal=self.goal_var.get(),
            depth_limit=self.depth_var.get(),
        )

    def _on_method_change(self, _event=None):
        if self.method_var.get() == 'Profundidade Limitada':
            self._depth_frame.pack(padx=16, pady=4, fill='x')
        else:
            self._depth_frame.pack_forget()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _section(self, text: str):
        tk.Label(self, text=text, font=self._fonts['section'],
                 bg=COLORS['panel'], fg=COLORS['accent2'],
                 anchor='w').pack(padx=16, pady=(10, 2), fill='x')

    def _divider(self):
        tk.Frame(self, bg=COLORS['panel_border'], height=1).pack(
            fill='x', padx=12, pady=6)

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
                  foreground=[('readonly', COLORS['text'])])
