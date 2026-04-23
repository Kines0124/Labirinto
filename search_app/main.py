"""
main.py
=======
Ponto de entrada da aplicação.

Responsabilidade única: instanciar a janela, criar os widgets,
conectar os callbacks e iniciar o loop de eventos.

Não contém lógica de busca, desenho de grafo nem estilos visuais —
cada uma dessas responsabilidades vive no módulo correspondente.
"""

import tkinter as tk
from tkinter import font

import config
from config import COLORS, WINDOW
from algorithms import run_search
from ui.graph_canvas import GraphCanvas
from ui.control_panel import ControlPanel
from ui.result_panel import ResultPanel


class SearchApp(tk.Tk):
    """
    Orquestrador principal da aplicação.

    Cria os três widgets (ControlPanel, GraphCanvas, ResultPanel),
    injeta os callbacks e trata os eventos de alto nível
    (executar busca, limpar).
    """

    def __init__(self):
        super().__init__()
        self.title(WINDOW['title'])
        self.configure(bg=COLORS['bg'])
        self.resizable(True, True)
        self.minsize(WINDOW['min_width'], WINDOW['min_height'])

        self._fonts = self._create_fonts()
        self._build_ui()
        self._center_window()

    # ── criação das fontes ────────────────────────────────────────────────────

    def _create_fonts(self) -> dict:
        return {
            'title':   font.Font(family='Courier', size=13, weight='bold'),
            'label':   font.Font(family='Courier', size=9),
            'section': font.Font(family='Courier', size=8,  weight='bold'),
            'mono':    font.Font(family='Courier', size=9),
            'big':     font.Font(family='Courier', size=22, weight='bold'),
            'node':    font.Font(family='Courier', size=11, weight='bold'),
        }

    # ── construção da UI ─────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()

        body = tk.Frame(self, bg=COLORS['bg'])
        body.pack(fill='both', expand=True)

        # painel esquerdo
        self.control = ControlPanel(
            body,
            on_search=self._handle_search,
            on_reset=self._handle_reset,
            on_regenerate=self._handle_regenerate,
            on_clear_path=lambda: self.graph_canvas.clear_path(),
            on_clear_result=lambda: self.result.clear(),
            on_pick_start=lambda: self.graph_canvas.set_pick_mode('start'),
            on_pick_goal=lambda: self.graph_canvas.set_pick_mode('goal'),
            fonts=self._fonts,
        )
        self.control.pack(side='left', fill='y', padx=(8, 4), pady=8)

        # canvas central
        canvas_wrapper = tk.Frame(body, bg=COLORS['bg'])
        canvas_wrapper.pack(side='left', fill='both', expand=True, padx=4, pady=8)
        tk.Label(canvas_wrapper, text='GRAFO DO PROBLEMA',
                 font=self._fonts['section'],
                 bg=COLORS['bg'], fg=COLORS['text_dim'],
                 anchor='w').pack(padx=4, pady=(4, 0))

        self.graph_canvas = GraphCanvas(canvas_wrapper,
                                on_regenerate=self._handle_regenerate,
                                on_node_picked=self._handle_node_picked)
        self.graph_canvas.set_fonts(self._fonts)
        self.graph_canvas.pack(fill='both', expand=True)

        # painel direito
        self.result = ResultPanel(body, fonts=self._fonts)
        self.result.pack(side='right', fill='y', padx=(4, 8), pady=8)

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS['panel'], height=48)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        tk.Label(header, text='◈  TREE SEARCH VISUALIZER',
                 font=self._fonts['title'],
                 bg=COLORS['panel'], fg=COLORS['accent'],
                 ).pack(side='left', padx=20, pady=10)
        tk.Label(header, text='IA · Algoritmos de Busca',
                 font=self._fonts['label'],
                 bg=COLORS['panel'], fg=COLORS['text_dim'],
                 ).pack(side='right', padx=20)

    def _center_window(self):
        self.update_idletasks()
        w, h = WINDOW['width'], WINDOW['height']
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    # ── callbacks ────────────────────────────────────────────────────────────

    def _handle_search(self, method: str, start: str,
                       goal: str, depth_limit: int,
                       heuristic_name: str = 'manhattan'):
        if start == goal:
            self.result.set_status('⚠ Estado inicial = objetivo.',
                                   COLORS['warning'])
            return

        self.result.set_status(f'Executando {method}...', COLORS['accent'])
        self.update()

        result = run_search(
            method=method,
            start=start,
            goal=goal,
            graph=config.GRAPH,
            heuristic=None,
            depth_limit=depth_limit,
            heuristic_name=heuristic_name,
        )
        
        self.graph_canvas.render(path=result.path, start=start, goal=goal)
        self.result.update_result(result)

        if result.found:
            self.result.set_status(
                f'✓ Caminho encontrado! {len(result.path)} nós.',
                COLORS['success'])
        else:
            self.result.set_status('✗ Sem caminho encontrado.',
                                   COLORS['danger'])

    def _handle_node_picked(self, role: str, node: str):
        """Recebe o nó clicado no canvas e atualiza o combobox correspondente."""
        self.control.set_pick_active(None)  # apaga destaque do botão
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

    def _handle_reset(self):
        start = self.control.start_var.get()
        goal  = self.control.goal_var.get()
        self.graph_canvas.render(start=start, goal=goal)
        self.result.clear()

    def _handle_regenerate(self):
        config.regenerate_maze()
        self.control.start_var.set(config.STATES[0])
        self.control.goal_var.set(config.STATES[-1])
        self.graph_canvas.render()
        self.result.clear()


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = SearchApp()
    app.mainloop()