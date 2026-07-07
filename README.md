# Labirinto

<div align = "center">

<img src = "/resources/logo.png" alt = "Labirinto logo" title = "racoons">

Interactive visualizer for search algorithms in artificial intelligence, developed as an academic project. The maze is procedurally generated on each run and traversed by the implemented algorithms, allowing visual comparison of search strategies in terms of solution cost and depth.

</div>

---

## 📋 Table of Contents

* [Overview](#overview-dart)
* [How the Maze Is Generated](#how-the-maze-is-generated-mag_right)
    - [How It Works](#how-it-works)
* [Terrains and Weights](#terrains-and-weights-four_leaf_clover)
* [Implemented Algorithms](#implemented-algorithms-bulb)
    - [Uninformed Search](#uninformed-search)
    - [Informed (Heuristic) Search](#informed-heuristic-search)
    - [Available Heuristics](#available-heuristics)
* [Interface](#interface-computer)
* [Requirements](#requirements-pushpin)
* [How to Run](#how-to-run-rocket)
* [Credits](#credits-tada)

---

## Overview :dart:

The application displays a grid-based maze represented as a **weighted graph**. The user chooses a start state, a goal state, and a search algorithm. The visualizer runs the algorithm and highlights the found path in the graph, showing the total cost and depth of the solution.

Every time the program is started (or when the **⟳ NEW MAZE** button is pressed), a different maze is generated — ensuring the algorithms are evaluated on varied scenarios.

---

## How the Maze Is Generated :mag_right:

The maze is generated using a **randomized version inspired by Kruskal's algorithm**. Unlike a classic "perfect maze" (which has no cycles and exactly one path between any two points), this generator deliberately allows cycles, so that different algorithms can produce visibly different paths and cost/depth trade-offs become meaningful to compare.

### How It Works

1. All cells start isolated (all walls active).
2. All possible edges between neighboring cells are generated and **randomly shuffled**.
3. For each edge `(u, v)`: if `u` and `v` belong to different components (checked via **Union-Find with path compression and union by rank**), the wall between them is removed and the components are merged.
4. The process repeats until all cells belong to the same component.

The logical maze has **8×8 cell** dimensions. To represent walls explicitly, a 2-to-1 expansion is used, resulting in an **expanded 15×15 grid**.

> On top of this Kruskal-inspired base structure, the generator adds extra passages with a configurable probability (`EXTRA_EDGE_PROBABILITY = 0.45`). These extra edges intentionally introduce cycles, making the maze less rigid — and giving algorithms that consider cost (like UCS) genuinely different paths to choose between, rather than the single unique path a perfect maze would offer.

To reproduce a specific maze, set `MAZE_SEED` in `config.py` to an integer value.

---

## Terrains and Weights :four_leaf_clover:

Each free cell in the maze is randomly assigned a terrain type. Terrain weights affect traversal cost and are relevant for algorithms that take cost into account (UCS, A*, Greedy, IDA*).

| Terrain    | Symbol      | Weight | Probability |
|------------|-------------|--------|-------------|
| Plain      | ■ light     | 1      | 50%         |
| Forest     | ■ green     | 2      | 25%         |
| Swamp      | ■ olive     | 3      | 15%         |
| Mountain   | ■ dark      | 5      | 10%         |

---

## Implemented Algorithms :bulb:

### Uninformed Search

| Algorithm | Description |
|-----------|-------------|
| **Breadth-First Search (BFS)** | Explores level by level; guarantees the fewest steps, but ignores weights. |
| **Depth-First Search (DFS)** | Explores depth-first; does not guarantee optimality, may not terminate on graphs with cycles. |
| **Depth-Limited Search (DLS)** | DFS variant with a configurable depth limit. |
| **Iterative Deepening (IDDFS)** | Combines DFS's memory efficiency with BFS's completeness. |
| **Bidirectional Search** | Searches simultaneously from the start and the goal; meets in the middle. |
| **Uniform Cost Search (UCS)** | Expands the node with the lowest accumulated cost; optimal for weighted graphs. |

### Informed (Heuristic) Search

| Algorithm | Description |
|-----------|-------------|
| **Greedy Best-First** | Guided only by the heuristic; fast, but does not guarantee optimality. |
| **A\* (A-star)** | Combines actual cost and heuristic; optimal and complete with an admissible heuristic. |
| **IDA\* (Iterative Deepening A\*)** | Iterative deepening variant of A*; uses less memory than A*. |

### Available Heuristics

For informed algorithms, the user can choose between:

- **Manhattan** *(default)*: sum of horizontal and vertical distances to the goal. Admissible and efficient for orthogonal grids.
- **Euclidean**: Calculated using the Pythagorean theorem, it guarantees finding the shortest path as long as it never overestimates the true distance.
- **Dijkstra (real)**: runs reverse Dijkstra from the goal to compute the exact minimum cost to each node. A perfect heuristic — never overestimates.

---

## Interface :computer:

The interface is divided into three panels:

**Left panel — Controls**
- Search method selection
- Heuristic selection (automatically shown for Greedy, A*, and IDA*)
- Depth limit (shown for DLS and IDDFS)
- Start and goal state selection
- Buttons: Run, Clear, New Maze
- Color and terrain legend

**Center panel — Graph**
- Visualization of the maze as a grid colored by terrain
- Highlight of the found path in purple
- Marking of the start state (blue) and goal state (green)

**Right panel — Result**
- Total cost of the solution
- Depth of the solution
- Full sequence of nodes in the path
- Execution status bar

---

## Requirements :pushpin:

- **Python 3.10 or higher** (tested with Python 3.11)
- **tkinter** — included in the standard Python installation on Windows and macOS
- **Pillow** — for rendering tilesets and spritesheets

> **Linux:** tkinter and Pillow may need to be installed separately:
> ```bash
> # Ubuntu/Debian
> sudo apt install python3-tk
> sudo apt install python3-pil.imagetk
>
> # Fedora
> sudo dnf install python3-tkinter
>
> # Arch Linux
> sudo pacman -S tk
> ```

Install the external dependencies with:
```bash
pip install pillow
```

---

## How to Run :rocket:

**1. Clone or download the repository**

```bash
git clone <repository-url>
cd Labirinto
```

**2. Check your Python version**

```bash
python --version
# or
python3 --version
```

The version must be **3.10 or higher**.

**3. Run the application**

```bash
cd search_app
python main.py
```

> On some systems, use `python3` instead of `python`.

**4. (Optional) Pin a specific maze**

To always load the same maze, edit the line in `search_app/config.py`:

```python
MAZE_SEED: Optional[int] = None   # Change None to an integer, e.g.: 42
```

---

## Credits :tada:

**Maze Generation**

The randomized Kruskal-based algorithm used for maze generation is based on the article:

> **Jamis Buck** — *"Maze Generation: Kruskal's Algorithm"*  
> The Buckblog, January 3, 2011  
> [https://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm](https://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm)

The article describes how to adapt Kruskal's algorithm — originally designed for minimum spanning trees in weighted graphs — for generating perfect mazes, replacing lowest-weight selection with random edge selection. The Union-Find structure used to detect connected components is also detailed in the article. This project extends that base by additionally allowing extra edges (and thus cycles), as described above.