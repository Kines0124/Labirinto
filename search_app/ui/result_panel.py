"""
ui/result_panel.py
==================
Right panel of the interface: displays cost, path found, and status bar.
"""

import  tkinter         as tk
from    tkinter         import font as tkfont
from    config           import COLORS
from    search_result    import SearchResult
from    i18n              import t


class ResultPanel(tk.Frame):
    """Right-side panel with cost, path found, and status bar."""

    def __init__(self, parent, fonts: dict, **kwargs):
        """Initializes the panel and builds the result widgets."""
        super().__init__(parent, bg=COLORS['panel'], width=230,
                         highlightbackground=COLORS['panel_border'],
                         highlightthickness=1, **kwargs)
        self.pack_propagate(False)
        self._fonts = fonts
        self._build()

    # ── build ────────────────────────────────────────────────────────────────

    def _build(self):
        """Builds the cost, stats, path, and status widgets."""
        self._result_section_lbl = self._section('result_section')

        # ── total cost ──
        cost_box = tk.Frame(self, bg=COLORS['node_default'],
                            highlightbackground=COLORS['panel_border'],
                            highlightthickness=1)
        cost_box.pack(padx=14, pady=(4, 8), fill='x')
        self._total_cost_lbl = tk.Label(cost_box, text=t('total_cost_label'),
                 font=self._fonts['section'],
                 bg=COLORS['node_default'],
                 fg=COLORS['text_dim'])
        self._total_cost_lbl.pack(pady=(8, 0))
        self._cost_lbl = tk.Label(cost_box, text='—',
                                  font=self._fonts['big'],
                                  bg=COLORS['node_default'],
                                  fg=COLORS['warning'])
        self._cost_lbl.pack(pady=(0, 8))

        # ── stats ──
        stats = tk.Frame(self, bg=COLORS['panel'])
        stats.pack(padx=14, fill='x')
        self._depth_stat_lbl, self._depth_lbl = self._stat_box(stats, 'depth_stat_label')

        # ── path ──
        self._divider()
        self._path_section_lbl = self._section('path_found_section')

        path_frame = tk.Frame(self, bg=COLORS['node_default'],
                              highlightbackground=COLORS['panel_border'],
                              highlightthickness=1)
        path_frame.pack(padx=14, pady=4, fill='both', expand=True)

        scrollbar = tk.Scrollbar(path_frame, orient='vertical',
                                 bg=COLORS['panel_border'])
        self._path_text = tk.Text(path_frame,
                                  font=self._fonts['mono'],
                                  bg=COLORS['node_default'],
                                  fg=COLORS['text'],
                                  relief='flat', wrap='word',
                                  state='disabled',
                                  insertbackground=COLORS['text'],
                                  yscrollcommand=scrollbar.set,
                                  padx=8, pady=8)
        scrollbar.config(command=self._path_text.yview)
        scrollbar.pack(side='right', fill='y')
        self._path_text.pack(side='left', fill='both', expand=True)

        # ── status ──
        self._divider()
        self._status_lbl = tk.Label(self, text=t('waiting_status'),
                                    font=self._fonts['section'],
                                    bg=COLORS['panel'],
                                    fg=COLORS['text_dim'],
                                    anchor='w', wraplength=200, justify='left')
        self._status_lbl.pack(padx=14, pady=(4, 10), anchor='w')

        # cache the last result so refresh_texts() can redraw the path text
        # (with translated "Total cost:"/"Depth:" lines) after a language switch
        self._last_result: SearchResult | None = None

    # ── public API ───────────────────────────────────────────────────────────

    def update_result(self, result: SearchResult):
        """Updates all widgets with the SearchResult data."""
        self._last_result = result
        self._render_result(result)

    def clear(self):
        """Resets the panel to its initial state."""
        self._last_result = None
        self._cost_lbl.config(text='—', fg=COLORS['warning'])
        self._depth_lbl.config(text='—')
        self._path_text.config(state='normal')
        self._path_text.delete('1.0', 'end')
        self._path_text.config(state='disabled')
        self.set_status(t('waiting_status'), COLORS['text_dim'])

    def set_status(self, message: str, color: str = None):
        """Displays a message in the status bar with the given color."""
        color = color or COLORS['text_dim']
        self._status_lbl.config(text=message, fg=color)

    def refresh_texts(self):
        """Re-applies translated strings to every static widget after a
        language change, and re-renders the last result (if any) so the
        path panel's "Total cost:"/"Depth:" lines switch language too."""
        self._result_section_lbl.config(text=t('result_section'))
        self._total_cost_lbl.config(text=t('total_cost_label'))
        self._depth_stat_lbl.config(text=t('depth_stat_label'))
        self._path_section_lbl.config(text=t('path_found_section'))

        if self._last_result is not None:
            self._render_result(self._last_result)
        else:
            self.set_status(t('waiting_status'), COLORS['text_dim'])

    # ── helpers ──────────────────────────────────────────────────────────────

    def _render_result(self, result: SearchResult):
        """Draws a SearchResult into the cost/depth/path widgets."""
        path  = result.path
        cost  = result.cost
        depth = result.depth

        self._cost_lbl.config(
            text=str(cost) if result.found else '∞',
            fg=COLORS['warning'] if result.found else COLORS['danger'],
        )
        self._depth_lbl.config(text=str(depth))

        self._path_text.config(state='normal')
        self._path_text.delete('1.0', 'end')
        if result.found:
            self._path_text.insert('end', ' → '.join(path) + '\n\n')
            self._path_text.insert('end', t('total_cost_line', cost=cost))
            self._path_text.insert('end', t('depth_line', depth=depth))
        else:
            self._path_text.insert('end', t('no_path_found_text'))
        self._path_text.config(state='disabled')

    def _stat_box(self, parent, label_key: str) -> tuple[tk.Label, tk.Label]:
        """Creates and returns a stat box with a label and a value widget."""
        box = tk.Frame(parent, bg=COLORS['node_default'],
                       highlightbackground=COLORS['panel_border'],
                       highlightthickness=1)
        box.pack(side='left', expand=True, fill='both', padx=2)
        label_lbl = tk.Label(box, text=t(label_key), font=self._fonts['section'],
                 bg=COLORS['node_default'],
                 fg=COLORS['text_dim'])
        label_lbl.pack(pady=(6, 0))
        val_lbl = tk.Label(box, text='—',
                           font=tkfont.Font(family='Courier', size=14, weight='bold'),
                           bg=COLORS['node_default'],
                           fg=COLORS['accent'])
        val_lbl.pack(pady=(0, 6))
        return label_lbl, val_lbl

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