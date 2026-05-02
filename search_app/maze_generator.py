"""
maze_generator.py
=================
Geração procedural de labirintos com base no algoritmo de Kruskal.
"""

from    __future__  import annotations
import  random
from    dataclasses import dataclass, field
from    typing      import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Tipos de terreno
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TerrainType:
    name: str
    weight: float
    probability: float   # deve somar 1.0 no conjunto escolhido


TERRAINS: list[TerrainType] = [
    TerrainType("plains",   1.0, 0.50), # 50%
    TerrainType("forest",   2.0, 0.25), # 25%
    TerrainType("swamp",    3.0, 0.15), # 15%
    TerrainType("mountain", 5.0, 0.10), # 10%
]

# Validação simples
assert abs(sum(t.probability for t in TERRAINS) - 1.0) < 1e-6, \
    "Probabilidades dos terrenos devem somar 1.0"

EXTRA_EDGE_PROBABILITY: float = 0.45  # 0.0 = perfeito, 1.0 = remove todas as paredes

def _sample_terrain(rng: random.Random) -> TerrainType:
    """Sorteia um terreno conforme as probabilidades configuradas."""
    r = rng.random()
    cumulative = 0.0
    for terrain in TERRAINS:
        cumulative += terrain.probability
        if r < cumulative:
            return terrain
    return TERRAINS[-1]  # fallback


# ─────────────────────────────────────────────────────────────────────────────
# Union-Find (Disjoint Set Union — DSU)
# ─────────────────────────────────────────────────────────────────────────────

class UnionFind:
    """Estrutura Union-Find com compressão de caminho e união por rank."""

    def __init__(self, n: int):
        """Método Construtor."""
        self._parent = list(range(n))
        self._rank   = [0] * n

    def find(self, x: int) -> int:
        """Retorna o representante do componente de x (com compressão de caminho)."""
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]  # path halving
            x = self._parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        """
        Une os componentes de x e y.
        Retorna True se eram componentes distintos (a parede foi removida),
        False se já pertenciam ao mesmo componente.
        """
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        # União por rank
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Resultado da geração
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MazeResult:
    """Contém todos os dados gerados pelo algoritmo de Kruskal."""
    rows:         int
    cols:         int
    grid_map:     list[list[int]]
    grid_weights: list[list[float]]
    terrain_map:  list[list[Optional[TerrainType]]]
    seed:         int

    # dimensões reais do grid expandido
    @property
    def grid_rows(self) -> int:
        return 2 * self.rows - 1

    @property
    def grid_cols(self) -> int:
        return 2 * self.cols - 1


# ─────────────────────────────────────────────────────────────────────────────
# Algoritmo principal
# ─────────────────────────────────────────────────────────────────────────────

def generate_kruskal_maze(rows: int = 8,
                          cols: int = 8,
                          seed: Optional[int] = None,
                         ) -> MazeResult:
    """Gera um labirinto usando o algoritmo de Kruskal randomizado."""
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    rng = random.Random(seed)

    n_cells = rows * cols
    dsu = UnionFind(n_cells)

    def cell_id(r: int, c: int) -> int:
        return r * cols + c

    edges: list[tuple[int, int, int, int]] = []   # (r1, c1, r2, c2)
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                edges.append((r, c, r, c + 1))   # aresta horizontal
            if r + 1 < rows:
                edges.append((r, c, r + 1, c))   # aresta vertical

    rng.shuffle(edges)

    G_ROWS = 2 * rows - 1
    G_COLS = 2 * cols - 1

    grid_map:     list[list[int]]                   = [[1] * G_COLS for _ in range(G_ROWS)]
    terrain_map:  list[list[Optional[TerrainType]]] = [[None] * G_COLS for _ in range(G_ROWS)]

    # Marcar pixels de células como livres e sortear terreno
    for r in range(rows):
        for c in range(cols):
            gr, gc = 2 * r, 2 * c
            grid_map[gr][gc] = 0
            terrain_map[gr][gc] = _sample_terrain(rng)

    for r1, c1, r2, c2 in edges:
        united = dsu.union(cell_id(r1, c1), cell_id(r2, c2))
        if united or rng.random() < EXTRA_EDGE_PROBABILITY:
            wr, wc = r1 + r2, c1 + c2
            grid_map[wr][wc] = 0
            terrain_map[wr][wc] = terrain_map[2 * r2][2 * c2]

    grid_weights: list[list[float]] = []
    for r in range(G_ROWS):
        row_w: list[float] = []
        for c in range(G_COLS):
            if grid_map[r][c] == 1:
                row_w.append(0.0)          # parede — peso irrelevante
            else:
                t = terrain_map[r][c]
                row_w.append(t.weight if t is not None else 1.0)
        grid_weights.append(row_w)

    return MazeResult(
        rows=rows,
        cols=cols,
        grid_map=grid_map,
        grid_weights=grid_weights,
        terrain_map=terrain_map,
        seed=seed,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Conversão para o formato esperado por config.py / _build_graph
# ─────────────────────────────────────────────────────────────────────────────

def maze_to_config_format(result: MazeResult,
                         ) -> tuple[list[list[int]], list[list[float]], int, int]:
    """Converte um MazeResult para as estruturas usadas em config.py."""
    return (
        result.grid_map,
        result.grid_weights,
        result.grid_rows,
        result.grid_cols,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Utilitários de debug / inspeção
# ─────────────────────────────────────────────────────────────────────────────

_TERRAIN_CHAR: dict[str, str] = {
    "plains":   ".",
    "forest":   "F",
    "swamp":    "S",
    "mountain": "M",
}

def print_maze(result: MazeResult) -> None:
    """Imprime o labirinto no terminal para inspeção rápida."""
    G_ROWS = result.grid_rows
    G_COLS = result.grid_cols
    print(f"Seed: {result.seed}  |  Labirinto lógico: {result.rows}×{result.cols}"
          f"  |  Grid expandido: {G_ROWS}×{G_COLS}")
    print("+" + "─" * (G_COLS * 2 - 1) + "+")
    for r in range(G_ROWS):
        row_str = ""
        for c in range(G_COLS):
            if result.grid_map[r][c] == 1:
                row_str += "██"
            else:
                t = result.terrain_map[r][c]
                ch = _TERRAIN_CHAR.get(t.name, "?") if t else "?"
                row_str += f"{ch} "
        print(f"|{row_str.rstrip()}|")
    print("+" + "─" * (G_COLS * 2 - 1) + "+")


def terrain_stats(result: MazeResult) -> dict[str, int]:
    """Conta quantas células de cada terreno foram geradas."""
    counts: dict[str, int] = {t.name: 0 for t in TERRAINS}
    for r in range(result.grid_rows):
        for c in range(result.grid_cols):
            if result.grid_map[r][c] == 0:
                t = result.terrain_map[r][c]
                if t:
                    counts[t.name] = counts.get(t.name, 0) + 1
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# Execução standalone — teste rápido
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    maze = generate_kruskal_maze(rows=8, cols=8, seed=42)
    print_maze(maze)
    print("\nEstatísticas de terreno:")
    for name, count in terrain_stats(maze).items():
        print(f"  {name:10s}: {count:3d} células")

    grid_map, grid_weights, g_rows, g_cols = maze_to_config_format(maze)
    print(f"\ngrid_map[0]     = {grid_map[0]}")
    print(f"grid_weights[0] = {grid_weights[0]}")