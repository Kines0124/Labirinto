# Labirinto

Visualizador interativo de algoritmos de busca em inteligência artificial, desenvolvido como projeto acadêmico. O labirinto é gerado proceduralmente a cada execução e percorrido pelos algoritmos implementados, permitindo comparar visualmente as estratégias de busca em termos de custo e profundidade da solução.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Como o Labirinto é Gerado](#como-o-labirinto-é-gerado)
- [Terrenos e Pesos](#terrenos-e-pesos)
- [Algoritmos Implementados](#algoritmos-implementados)
- [Interface](#interface)
- [Requisitos](#requisitos)
- [Como Rodar](#como-rodar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Créditos](#créditos)

---

## Visão Geral

A aplicação exibe um labirinto em grade representado como um **grafo ponderado**. O usuário escolhe um estado inicial, um estado objetivo e um algoritmo de busca. O visualizador executa o algoritmo e destaca o caminho encontrado no grafo, exibindo o custo total e a profundidade da solução.

A cada vez que o programa é iniciado (ou quando o botão **⟳ NOVO LABIRINTO** é pressionado), um labirinto diferente é gerado — garantindo que os algoritmos sejam avaliados em cenários variados.

---

## Como o Labirinto é Gerado

O labirinto é gerado por uma **versão aleatorizada do algoritmo de Kruskal**, que produz labirintos perfeitos — estruturas sem ciclos onde existe exatamente um caminho entre quaisquer dois pontos.

### Funcionamento

1. Todas as células são inicializadas isoladas (todas as paredes ativas).
2. Todas as arestas possíveis entre células vizinhas são geradas e **embaralhadas aleatoriamente**.
3. Para cada aresta `(u, v)`: se `u` e `v` pertencem a componentes distintos (verificado via **Union-Find com compressão de caminho e união por rank**), a parede entre eles é removida e os componentes são unidos.
4. O processo se repete até que todas as células pertençam ao mesmo componente.

O labirinto lógico tem dimensões **8×8 células**. Para representar as paredes de forma explícita, é utilizada uma expansão 2-para-1, resultando em um **grid expandido de 15×15**.

> Além de garantir a conectividade total, o gerador adiciona passagens extras com uma probabilidade configurável (`EXTRA_EDGE_PROBABILITY = 0.45`), tornando o labirinto menos rígido e mais interessante para algoritmos de custo uniforme.

Para reproduzir um labirinto específico, defina `MAZE_SEED` em `config.py` com um valor inteiro.

---

## Terrenos e Pesos

Cada célula livre do labirinto recebe um tipo de terreno sorteado aleatoriamente. Os pesos dos terrenos influenciam o custo de travessia e são relevantes para algoritmos que consideram custo (UCS, A\*, Greedy, IDA\*).

| Terreno   | Símbolo | Peso | Probabilidade |
|-----------|---------|------|---------------|
| Planície  | ■ claro | 1    | 50%           |
| Floresta  | ■ verde | 2    | 25%           |
| Pântano   | ■ oliva | 3    | 15%           |
| Montanha  | ■ escuro| 5    | 10%           |

---

## Algoritmos Implementados

### Busca Não-Informada

| Algoritmo | Descrição |
|-----------|-----------|
| **Amplitude (BFS)** | Explora em largura; garante o menor número de passos, mas ignora pesos. |
| **Profundidade (DFS)** | Explora em profundidade; não garante otimalidade, pode não terminar em grafos com ciclos. |
| **Profundidade Limitada (DLS)** | Variante do DFS com limite de profundidade configurável. |
| **Aprofundamento Iterativo (IDDFS)** | Combina economia de memória do DFS com completude do BFS. |
| **Bidirecional** | Busca simultânea a partir do início e do objetivo; encontra-se no meio. |
| **Custo Uniforme (UCS)** | Expande o nó de menor custo acumulado; ótimo para grafos ponderados. |

### Busca Informada (Heurística)

| Algoritmo | Descrição |
|-----------|-----------|
| **Greedy Best-First** | Guia-se apenas pela heurística; rápido, mas não garante otimalidade. |
| **A\* (A-estrela)** | Combina custo real e heurística; ótimo e completo com heurística admissível. |
| **IDA\* (A\* Iterativo)** | Variante do A\* com aprofundamento iterativo; usa menos memória que o A\*. |

### Heurísticas disponíveis

Para os algoritmos informados, o usuário pode escolher entre:

- **Manhattan** *(padrão)*: soma das distâncias horizontais e verticais até o objetivo. Admissível e eficiente para grades ortogonais.
- **Dijkstra (real)**: roda Dijkstra reverso a partir do objetivo para calcular o custo mínimo exato até cada nó. Heurística perfeita — nunca superestima.

---

## Interface

A interface é dividida em três painéis:

**Painel esquerdo — Controle**
- Seleção do método de busca
- Seleção da heurística (aparece automaticamente para Greedy, A\* e IDA\*)
- Limite de profundidade (aparece para DLS e IDDFS)
- Seleção de estado inicial e objetivo
- Botões: Executar, Limpar, Novo Labirinto
- Legenda de cores e terrenos

**Painel central — Grafo**
- Visualização do labirinto como grade colorida por terreno
- Destaque do caminho encontrado em roxo
- Marcação do estado inicial (azul) e objetivo (verde)

**Painel direito — Resultado**
- Custo total da solução
- Profundidade da solução
- Sequência completa de nós do caminho
- Barra de status da execução

---

## Requisitos

- **Python 3.10 ou superior** (testado com Python 3.11)
- **tkinter** — incluso na instalação padrão do Python no Windows e macOS
- **Pillow** — para renderização dos tilesets e spritesheets

> **Linux:** tkinter e Pillow podem precisar ser instalados separadamente:
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

Instale as dependências externas com:
```bash
pip install pillow
```

---

## Como Rodar

### 1. Clone ou baixe o repositório

```bash
git clone <url-do-repositorio>
cd Labirinto
```

### 2. Verifique sua versão do Python

```bash
python --version
# ou
python3 --version
```

A versão deve ser **3.10 ou superior**.

### 3. Execute a aplicação

```bash
cd search_app
python main.py
```

> Em alguns sistemas, use `python3` em vez de `python`.

### 4. (Opcional) Fixar um labirinto específico

Para sempre carregar o mesmo labirinto, edite a linha em `search_app/config.py`:

```python
MAZE_SEED: Optional[int] = None   # Altere None para um inteiro, ex.: 42
```

---

## Estrutura do Projeto

```
Labirinto/
└── search_app/
    ├── main.py              # Ponto de entrada; orquestra a aplicação
    ├── config.py            # Configurações globais (cores, janela, grafo)
    ├── maze_generator.py    # Geração do labirinto via Kruskal aleatorizado
    ├── search_result.py     # Dataclass com o resultado de cada busca
    ├── algorithms/
    │   ├── __init__.py      # Registro central dos algoritmos (run_search)
    │   ├── heuristica.py    # Heurísticas: Manhattan e Dijkstra reverso
    │   ├── bfs.py           # Busca em Largura
    │   ├── dfs.py           # Busca em Profundidade
    │   ├── dls.py           # Profundidade Limitada
    │   ├── iddfs.py         # Aprofundamento Iterativo
    │   ├── bidi.py          # Busca Bidirecional
    │   ├── ucs.py           # Custo Uniforme
    │   ├── greedy.py        # Greedy Best-First
    │   ├── astar.py         # A* (A-estrela)
    │   ├── ida_star.py      # IDA* (A* Iterativo)
    │   ├── BuscaNP.py       # Infraestrutura de busca não-informada
    │   ├── BuscaP.py        # Infraestrutura de busca informada
    │   ├── Node.py          # Nó para buscas não-informadas
    │   ├── NodeP.py         # Nó para buscas informadas (com custo)
    │   └── conversor.py     # Converte o grafo do config para o formato dos algoritmos
    └── ui/
        ├── control_panel.py # Painel esquerdo de controle
        ├── graph_canvas.py  # Visualização do labirinto em canvas
        └── result_panel.py  # Painel direito de resultados
```

---

## Créditos

### Geração do Labirinto

A implementação do algoritmo de Kruskal aleatorizado para geração de labirintos é baseada no artigo:

> **Jamis Buck** — *"Maze Generation: Kruskal's Algorithm"*  
> The Buckblog, 3 de janeiro de 2011  
> [https://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm](https://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm)

O artigo descreve como adaptar o algoritmo de Kruskal — originalmente para árvores geradoras mínimas em grafos ponderados — para a geração de labirintos perfeitos, substituindo a seleção por menor peso por uma seleção aleatória das arestas. A estrutura Union-Find utilizada para detectar componentes conectados também é detalhada no artigo.
