"""
i18n.py
=======
Centralized translation strings and language state for the application.

Usage:
    from i18n import t, set_language, get_language

    label.config(text=t('exit'))
    set_language('en')
"""

import config


# --------------------------------------------------------------------------
# TRANSLATION TABLE
# --------------------------------------------------------------------------
# Add new keys here as more of the UI gets localized (control_panel.py,
# result_panel.py, graph_canvas.py, ...). Keep both languages in sync —
# a missing key falls back to the key name itself (see t() below).
STRINGS = {
    'pt': {
        # header
        'window_title':        '◈  LABIRINTO  ◈',
        'exit':                '✕  Sair',
        'about':                'ℹ  Sobre',
        'settings':             '⚙  Config',

        # main canvas
        'generated_maze':       'LABIRINTO GERADO',

        # search status messages
        'start_equals_goal':    '⚠ Estado inicial = objetivo.',
        'running_method':       'Executando {method}...',
        'path_found':           '✓ Caminho encontrado! {n} nós.',
        'no_path_found':        '✗ Sem caminho encontrado.',
        'generating_multiverse':'Gerando multiverso...',
        'multiverse_generated': '✓ Multiverso gerado: {n_maps} mapas, {n_portals} portais.',

        # settings dialog
        'settings_title':       'Configurações',
        'settings_header':      '◈  CONFIGURAÇÕES  ◈',
        'language_label':       'Idioma',
        'language_pt':          'Português',
        'language_en':          'English',
        'close':                'Fechar',

        # control panel — sections
        'search_method_section':     '▸ MÉTODO DE BUSCA',
        'start_state_section':       '▸ ESTADO INICIAL',
        'goal_state_section':        '▸ ESTADO OBJETIVO',
        'multiverse_section':        '▸ MULTIVERSO',

        # control panel — fields and buttons
        'depth_limit_label':         'Limite de Profundidade:',
        'max_depth_label':           'Profundidade Máxima:',
        'heuristic_label':           'Heurística:',
        'run_search_btn':            '▶  EXECUTAR BUSCA',
        'clear_btn':                 '↺  LIMPAR',
        'new_maze_btn':              '⟳  NOVO LABIRINTO',
        'path_animation_label':      'Animação do caminho',
        'num_maps_label':            'Nº de mapas:',
        'portal_cost_label':         'Custo do portal:',
        'generate_multiverse_btn':   '🌀  GERAR MULTIVERSO',
        'exit_multiverse_btn':       '✕  SAIR DO MULTIVERSO',
        'legend_btn':                '◈  LEGENDA / TERRENOS',

        # legend popup
        'legend_title':              'Legenda',
        'states_transitions_section':'▸ ESTADOS E TRANSIÇÕES',
        'start_state_item':          'Estado inicial',
        'goal_state_item':           'Estado objetivo',
        'path_found_item':           'Caminho encontrado',
        'map_portal_item':           'Portal de mapa',
        'terrains_section':          '▸ TERRENOS',
        'terrain_plains':            'Planície  (peso 1)',
        'terrain_forest':            'Floresta  (peso 2)',
        'terrain_swamp':             'Pântano   (peso 3)',
        'terrain_mountain':          'Montanha  (peso 5)',
        'terrain_wall':              'Parede    (bloqueio)',

        # result panel
        'result_section':            '▸ RESULTADO',
        'total_cost_label':          'CUSTO TOTAL',
        'depth_stat_label':          'PROF.\nSOLUÇÃO',
        'path_found_section':        '▸ CAMINHO ENCONTRADO',
        'waiting_status':            'Aguardando execução...',
        'total_cost_line':           'Custo total: {cost}\n',
        'depth_line':                'Profundidade: {depth}\n',
        'no_path_found_text':        'Nenhum caminho encontrado.',

        # about dialog
        'about_window_title':        'Sobre',
        'about_header':              '◈  Sobre  ◈',
        'developed_by':              'DESENVOLVIDO POR',
        'about_description': (
            'Visualizador interativo de algoritmos de busca em inteligência artificial. '
            'O labirinto é gerado proceduralmente e percorrido por estratégias de busca '
            'para comparação de custo e profundidade em tempo real.'
        ),
        'assets_credit':             '\n\nASSETS E TILESETS EM PIXEL ART APRESENTADOS SÃO DA AUTORIA DOS DESENVOLVEDORES',
        'repo_url':                  '\n\nPara mais informações acesse o repositório: ',
    },
    'en': {
        # header
        'window_title':        '◈  LABIRINTO  ◈',
        'exit':                '✕  Exit',
        'about':                'ℹ  About',
        'settings':             '⚙  Settings',

        # main canvas
        'generated_maze':       'GENERATED MAZE',

        # search status messages
        'start_equals_goal':    '⚠ Start state = goal.',
        'running_method':       'Running {method}...',
        'path_found':           '✓ Path found! {n} nodes.',
        'no_path_found':        '✗ No path found.',
        'generating_multiverse':'Generating multiverse...',
        'multiverse_generated': '✓ Multiverse generated: {n_maps} maps, {n_portals} portals.',

        # settings dialog
        'settings_title':       'Settings',
        'settings_header':      '◈  SETTINGS  ◈',
        'language_label':       'Language',
        'language_pt':          'Português',
        'language_en':          'English',
        'close':                'Close',

        # control panel — sections
        'search_method_section':     '▸ SEARCH METHOD',
        'start_state_section':       '▸ START STATE',
        'goal_state_section':        '▸ GOAL STATE',
        'multiverse_section':        '▸ MULTIVERSE',

        # control panel — fields and buttons
        'depth_limit_label':         'Depth Limit:',
        'max_depth_label':           'Max Depth:',
        'heuristic_label':           'Heuristic:',
        'run_search_btn':            '▶  RUN SEARCH',
        'clear_btn':                 '↺  CLEAR',
        'new_maze_btn':              '⟳  NEW MAZE',
        'path_animation_label':      'Path animation',
        'num_maps_label':            'Number of maps:',
        'portal_cost_label':         'Portal cost:',
        'generate_multiverse_btn':   '🌀  GENERATE MULTIVERSE',
        'exit_multiverse_btn':       '✕  EXIT MULTIVERSE',
        'legend_btn':                '◈  LEGEND / TERRAIN',

        # legend popup
        'legend_title':              'Legend',
        'states_transitions_section':'▸ STATES AND TRANSITIONS',
        'start_state_item':          'Start state',
        'goal_state_item':           'Goal state',
        'path_found_item':           'Path found',
        'map_portal_item':           'Map portal',
        'terrains_section':          '▸ TERRAIN',
        'terrain_plains':            'Plains    (weight 1)',
        'terrain_forest':            'Forest    (weight 2)',
        'terrain_swamp':             'Swamp     (weight 3)',
        'terrain_mountain':          'Mountain  (weight 5)',
        'terrain_wall':              'Wall      (blocked)',

        # result panel
        'result_section':            '▸ RESULT',
        'total_cost_label':          'TOTAL COST',
        'depth_stat_label':          'SOL.\nDEPTH',
        'path_found_section':        '▸ PATH FOUND',
        'waiting_status':            'Waiting for execution...',
        'total_cost_line':           'Total cost: {cost}\n',
        'depth_line':                'Depth: {depth}\n',
        'no_path_found_text':        'No path found.',

        # about dialog
        'about_window_title':        'About',
        'about_header':              '◈  About  ◈',
        'developed_by':              'DEVELOPED BY',
        'about_description': (
            'Interactive visualizer for artificial-intelligence search algorithms. '
            'The maze is procedurally generated and traversed by search strategies '
            'for real-time cost and depth comparison.'
        ),
        'assets_credit':             '\n\nTHE PIXEL-ART ASSETS AND TILESETS SHOWN WERE CREATED BY THE DEVELOPERS',
        'repo_url':                  '\n\nCheck the repository for more information: ',
    },
}

DEFAULT_LANGUAGE = 'pt'


# --------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------
def get_language() -> str:
    """Returns the currently active language code ('pt' or 'en').

    Session-only: reads from config.LANGUAGE if present, otherwise falls
    back to DEFAULT_LANGUAGE. Nothing is persisted to disk, so the
    language resets to the default every time the app restarts.
    """
    return getattr(config, 'LANGUAGE', DEFAULT_LANGUAGE)


def set_language(lang: str) -> None:
    """Sets the active language for the current session only.

    Stores the choice on config.LANGUAGE (in-memory attribute — add
    `LANGUAGE: str = 'pt'` to config.py if you want a documented default,
    but it isn't required since getattr() falls back safely).
    """
    if lang in STRINGS:
        config.LANGUAGE = lang


def t(key: str, **kwargs) -> str:
    """Returns the translated string for *key* in the current language.

    Falls back to Portuguese if the key is missing in the active language,
    and to the raw key name if it's missing everywhere (so untranslated
    strings are obvious in the UI instead of raising an exception).
    Any kwargs are used to .format() the template, e.g. t('running_method', method='A*').
    """
    lang = get_language()
    table = STRINGS.get(lang, STRINGS[DEFAULT_LANGUAGE])
    template = table.get(key) or STRINGS[DEFAULT_LANGUAGE].get(key, key)
    return template.format(**kwargs) if kwargs else template


# --------------------------------------------------------------------------
# SEARCH METHOD / HEURISTIC LABELS
# --------------------------------------------------------------------------
# run_search() and the rest of the algorithms package dispatch on the exact
# *canonical* strings below (the original pt labels from config.SEARCH_METHODS,
# and 'manhattan' / 'dijkstra' / 'euclidiana' for heuristics). Those canonical
# values NEVER change with the UI language — only the text shown in the
# combobox does. ControlPanel should display method_label(canonical) and
# convert the user's selection back with method_canonical(display_text)
# before calling on_search / run_search.
SEARCH_METHOD_LABELS = {
    'pt': {
        'Amplitude (BFS)':                  'Amplitude (BFS)',
        'Profundidade (DFS)':               'Profundidade (DFS)',
        'Profundidade Limitada':            'Profundidade Limitada',
        'Aprofundamento Iterativo (IDDFS)': 'Aprofundamento Iterativo (IDDFS)',
        'Bidirecional':                     'Bidirecional',
        'Custo Uniforme (UCS)':             'Custo Uniforme (UCS)',
        'Greedy Best-First':                'Greedy Best-First',
        'A* (A-estrela)':                   'A* (A-estrela)',
        'AIA* (A* Iterativo)':              'AIA* (A* Iterativo)',
    },
    'en': {
        'Amplitude (BFS)':                  'Breadth-First (BFS)',
        'Profundidade (DFS)':               'Depth-First (DFS)',
        'Profundidade Limitada':            'Depth-Limited',
        'Aprofundamento Iterativo (IDDFS)': 'Iterative Deepening (IDDFS)',
        'Bidirecional':                     'Bidirectional',
        'Custo Uniforme (UCS)':             'Uniform Cost (UCS)',
        'Greedy Best-First':                'Greedy Best-First',
        'A* (A-estrela)':                   'A* (A-star)',
        'AIA* (A* Iterativo)':              'IDA* (Iterative A*)',
    },
}

# Heuristic canonical ids match what heuristica.py / control_panel.py already
# use internally: 'manhattan', 'dijkstra', 'euclidiana' (kept in Portuguese —
# see the note in the heuristica.py translation about not renaming it without
# also updating every caller).
HEURISTIC_LABELS = {
    'pt': {
        'manhattan':  'Manhattan',
        'dijkstra':   'Dijkstra',
        'euclidiana': 'Euclidiana (Multiverso)',
    },
    'en': {
        'manhattan':  'Manhattan',
        'dijkstra':   'Dijkstra',
        'euclidiana': 'Euclidean (Multiverse)',
    },
}


def method_label(canonical: str) -> str:
    """Translates a canonical method key (from config.SEARCH_METHODS) into
    the display label for the current language."""
    lang = get_language()
    return SEARCH_METHOD_LABELS.get(lang, SEARCH_METHOD_LABELS[DEFAULT_LANGUAGE]).get(canonical, canonical)


def method_canonical(label: str) -> str:
    """Reverse lookup: display label (in *any* language) -> canonical key.
    Falls back to returning the input unchanged if not found, so an
    already-canonical value passed in is safe."""
    for table in SEARCH_METHOD_LABELS.values():
        for canonical, display in table.items():
            if display == label:
                return canonical
    return label


def heuristic_label(canonical: str) -> str:
    """Translates a canonical heuristic key ('manhattan' | 'dijkstra' |
    'euclidiana') into the display label for the current language."""
    lang = get_language()
    return HEURISTIC_LABELS.get(lang, HEURISTIC_LABELS[DEFAULT_LANGUAGE]).get(canonical, canonical)


def heuristic_canonical(label: str) -> str:
    """Reverse lookup: display label (in *any* language) -> canonical
    heuristic key. Falls back to 'manhattan' if not found, matching the
    previous default behavior in control_panel.py."""
    for table in HEURISTIC_LABELS.values():
        for canonical, display in table.items():
            if display == label:
                return canonical
    return 'manhattan'