"""
main.py
==============================================================
Main orchestrator of the application.
"""

import  webbrowser
import  tkinter     as tk
from    tkinter     import font
from    PIL         import Image, ImageTk
from    pathlib     import Path

import  config
from    config           import COLORS, WINDOW
from    algorithms       import run_search
from    multiverse       import generate_multiverse
from    ui.graph_canvas  import GraphCanvas
from    ui.control_panel import ControlPanel
from    ui.result_panel  import ResultPanel
from    i18n             import t, set_language, get_language


class SearchApp(tk.Tk):
    """Main application window; orchestrates the canvas, panels, and callbacks."""
 
    def __init__(self):
        """Initializes the window, fonts, internal state, and builds the UI."""
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
 
    # ── fonts ─────────────────────────────────────────────────────────────────
 
    def _create_fonts(self) -> dict:
        """Creates and returns the dictionary of fonts used throughout the UI."""
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
        """Builds the main layout: header, control panel, canvas, and result panel."""
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
            on_exit_multiverse=self._exit_multiverse,
            fonts=self._fonts,
        )
        self.control.pack(side='left', fill='y', padx=(8, 4), pady=8)
 
        canvas_wrapper = tk.Frame(body, bg=COLORS['bg'])
        canvas_wrapper.pack(side='left', fill='both', expand=True, padx=4, pady=8)
        self._maze_label = tk.Label(
            canvas_wrapper, text=t('generated_maze'),
            font=self._fonts['section'],
            bg=COLORS['bg'], fg=COLORS['text_dim'],
            anchor='w')
        self._maze_label.pack(padx=4, pady=(4, 0))
 
        self.graph_canvas = GraphCanvas(
            canvas_wrapper,
            on_node_picked=self._handle_node_picked,
            on_map_nav=self._handle_map_nav,
            on_map_switch=self._handle_map_switch,
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
        """Builds the top bar with the title and global action buttons."""
        header = tk.Frame(self, bg=COLORS['panel'], height=48)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
 
        self._title_label = tk.Label(
            header, text=t('window_title'),
            font=self._fonts['title'],
            bg=COLORS['panel'], fg=COLORS['accent'])
        self._title_label.pack(side='left', padx=20, pady=10)
 
        btn_style = dict(font=self._fonts['label'], relief='flat',
                         cursor='hand2', padx=14, pady=4)
 
        self._exit_btn = tk.Button(
            header, text=t('exit'),
            bg=COLORS['panel'], fg=COLORS['text_dim'],
            activebackground='#c0392b', activeforeground='#ffffff',
            command=self.destroy, **btn_style)
        self._exit_btn.pack(side='right', padx=(4, 16), pady=8)
 
        self._about_btn = tk.Button(
            header, text=t('about'),
            bg=COLORS['panel'], fg=COLORS['text_dim'],
            activebackground=COLORS['accent'], activeforeground='#ffffff',
            command=self._show_about, **btn_style)
        self._about_btn.pack(side='right', padx=4, pady=8)
 
        self._settings_btn = tk.Button(
            header, text=t('settings'),
            bg=COLORS['panel'], fg=COLORS['text_dim'],
            activebackground=COLORS['accent'], activeforeground='#ffffff',
            command=self._show_settings, **btn_style)
        self._settings_btn.pack(side='right', padx=4, pady=8)
 
    def _center_window(self):
        """Centers the window on the screen on startup."""
        self.update_idletasks()
        w, h = WINDOW['width'], WINDOW['height']
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')
 
    # ── settings / language ──────────────────────────────────────────────────
 
    def _show_settings(self):
        """Opens the settings popup (currently: language selection only)."""
        win = tk.Toplevel(self)
        win.title(t('settings_title'))
        win.resizable(False, False)
        win.configure(bg=COLORS['panel'])
        win.grab_set()

        w, h = 380, 190
        win.withdraw()
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        win.geometry(f'{w}x{h}+{x}+{y}')
        win.deiconify()

        tk.Label(win, text=t('settings_title'),
                 font=self._fonts['title'],
                 bg=COLORS['panel'], fg=COLORS['accent']).pack(pady=(18, 8))

        tk.Label(win, text=t('language_label'),
                 font=self._fonts['label'],
                 bg=COLORS['panel'], fg=COLORS['text']).pack(pady=(0, 12))

        btn_row = tk.Frame(win, bg=COLORS['panel'])
        btn_row.pack(pady=4)

        def _select(lang: str):
            """Applies the chosen language and refreshes both the main
            window AND this popup's own widgets immediately — otherwise
            the popup would only pick up the new language the next time
            it's opened."""
            self._apply_language(lang)
            win.destroy()

        def _lang_button(parent, label: str, lang_code: str):
            """Draws language button."""
            active = get_language() == lang_code
            return tk.Button(
                parent, text=label, font=self._fonts['label'],
                bg=COLORS['accent'] if active else COLORS['panel'],
                fg='#ffffff' if active else COLORS['text'],
                activebackground=COLORS['accent'], activeforeground='#ffffff',
                relief='flat', cursor='hand2', padx=16, pady=6,
                command=lambda: _select(lang_code))

        _lang_button(btn_row, 'English', 'en').pack(side='left', padx=6)
        _lang_button(btn_row, 'Português', 'pt').pack(side='left', padx=6) 

        tk.Button(win, text=t('close'),
                  font=self._fonts['label'],
                  bg=COLORS['panel'], fg=COLORS['text_dim'],
                  relief='flat', cursor='hand2',
                  command=win.destroy).pack(pady=14)
 
    def _apply_language(self, lang: str):
        """Switches the active language (session-only) and refreshes UI text."""
        set_language(lang)
        self._refresh_texts()
 
    def _refresh_texts(self):
        """Re-applies translated strings to every widget this window owns
        directly. Child panels (control/result/canvas) are notified too, if
        they expose a `set_language` / `refresh_texts` hook — this lets us
        wire up control_panel.py and result_panel.py later without changing
        this method again."""
        self.title(WINDOW['title'])
        self._title_label.config(text=t('window_title'))
        self._exit_btn.config(text=t('exit'))
        self._about_btn.config(text=t('about'))
        self._settings_btn.config(text=t('settings'))
        self._maze_label.config(text=t('generated_maze'))
 
        for panel in (self.control, self.result, self.graph_canvas):
            if hasattr(panel, 'refresh_texts'):
                panel.refresh_texts()
 
    # ── callbacks ─────────────────────────────────────────────────────────────
 
    def _handle_search(self, method: str, start: str,
                    goal: str, depth_limit: int,
                    heuristic_name: str = 'manhattan'):
        """Runs the search with the given parameters and updates the canvas and result."""
        config.ACTIVE_METHOD = method 
 
        if start == goal:
            self.result.set_status(t('start_equals_goal'), COLORS['warning'])
            return
 
        self.result.set_status(t('running_method', method=method), COLORS['accent'])
        self.update()
 
        graph = config.SUPER_GRAPH if config.MULTIVERSE_MODE else config.GRAPH
 
        if config.MULTIVERSE_MODE and heuristic_name == 'manhattan':
            effective_heuristic = 'euclidiana'
        else:
            effective_heuristic = heuristic_name
 
        result = run_search(
            method=method,
            start=start,
            goal=goal,
            graph=graph,
            heuristic=heuristic_name,
            depth_limit=depth_limit,
            heuristic_name=effective_heuristic,
        )
 
        # Clears visit history before starting a new animation
        self.graph_canvas.reset_visited()
 
        self.graph_canvas.render(path=result.path, start=start, goal=goal)
        self.result.update_result(result)
 
        self._last_path  = result.path
        self._last_start = start
        self._last_goal  = goal
 
        if result.found:
            self.result.set_status(
                t('path_found', n=len(result.path)),
                COLORS['success'])
        else:
            self.result.set_status(t('no_path_found'), COLORS['danger'])
 
    def _on_body_resize(self, event):
        """Resizes the background image when the window is resized."""
        if not hasattr(self, '_bg_pil_orig'):
            return
        from PIL import ImageTk
        self._bg_image = ImageTk.PhotoImage(
            self._bg_pil_orig.resize((event.width, event.height), Image.NEAREST))
        self._bg_label.config(image=self._bg_image)
 
    def _handle_regenerate(self):
        """Regenerates the simple maze or the multiverse depending on the active mode."""
        if config.MULTIVERSE_MODE and config.MULTIVERSE is not None:
            self._handle_regenerate_multiverse(
                n_maps = config.MULTIVERSE.n_maps,
                portal_cost = config.PORTAL_COST,
            )
        else:
            config.regenerate_maze()
            self.graph_canvas.reset_visited()
            self.control.refresh_states(
                config.STATES, config.START_NODE, config.GOAL_NODE)
            self.graph_canvas.render()
            self.result.clear()
 
    def _handle_regenerate_multiverse(self, n_maps: int, portal_cost: float):
        """Generates a new multiverse and updates the global state and UI."""
        config.PORTAL_COST = portal_cost
        self.result.set_status(t('generating_multiverse'), COLORS['accent'])
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
            t('multiverse_generated',
              n_maps=n_maps, n_portals=len(mv.portals)//2),
            COLORS['success'],
        )
 
    def _exit_multiverse(self):
        """Exits multiverse mode and regenerates a simple maze."""
        self.graph_canvas.reset_visited()  
        config.MULTIVERSE_MODE = False
        config.MULTIVERSE = None
        self._handle_regenerate()
 
    def _handle_map_switch(self, new_map_id: int):
        """Updates the active map when a portal is crossed during the animation."""
        if not config.MULTIVERSE_MODE or config.MULTIVERSE is None:
            return
        if 0 <= new_map_id < config.MULTIVERSE.n_maps:
            config._apply_active_map(new_map_id)
 
    def _handle_map_nav(self, delta: int):
        """Manually navigates between multiverse maps via the side arrows."""
        if not config.MULTIVERSE_MODE or config.MULTIVERSE is None:
            return
        new_id = config.ACTIVE_MAP_ID + delta
        if 0 <= new_id < config.MULTIVERSE.n_maps:
            config._apply_active_map(new_id)
            self.graph_canvas.render(
                path=self._last_path,
                start=self._last_start,
                goal=self._last_goal,
                static=True,            # ← fixed trail, no re-animation
            )
 
    def _handle_reset(self):
        """Redraws the map with no path, keeping the current start and goal."""
        start = self.control.start_var.get()
        goal  = self.control.goal_var.get()
        self.graph_canvas.render(start=start, goal=goal)
        self.result.clear()
 
    def _handle_node_picked(self, role: str, node: str):
        """Registers the clicked node as start or goal and redraws the map."""
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
        """Opens the window with information about the project."""
        win = tk.Toplevel(self)
        win.title(t('about_window_title'))
        win.resizable(False, False)
        win.configure(bg=COLORS['panel'])
        win.grab_set()

        w, h = 630, 480
        win.withdraw()
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        win.geometry(f'{w}x{h}+{x}+{y}')
        win.deiconify()

        font_family = self._fonts['label'].actual()['family']
        base_size   = self._fonts['label'].actual()['size']

        main_frame = tk.Frame(win, bg=COLORS['panel'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)

        tk.Label(main_frame, text=t('about_header'),
                 font=self._fonts['title'],
                 bg=COLORS['panel'], fg=COLORS['accent']
                 ).pack(pady=(10, 15))

        tk.Label(main_frame, text=t('developed_by'),
                 font=(font_family, base_size, 'bold'),
                 bg=COLORS['panel'], fg=COLORS['accent']).pack()
        
        tk.Label(main_frame,
                 text='Guilherme Carvalho Alvarenga & Lara Hydalgo Ferreira',
                 font=(self._fonts['label'], base_size + 2, 'bold'),
                 bg=COLORS['panel'], fg=COLORS['text']).pack(pady=(0, 20))

        tk.Label(main_frame, text=t('about_description'),
                 font=self._fonts['label'],
                 bg=COLORS['panel'], fg=COLORS['text'],
                 justify='left', wraplength=550
                 ).pack(pady=10)
        
        tk.Label(main_frame, text=t('assets_credit'),
                 font=(font_family, base_size, 'bold'),
                 bg=COLORS['panel'], fg=COLORS['accent']).pack()

        tk.Label(main_frame, text=t('repo_url'),
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

        tk.Button(main_frame, text=t('close'),
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