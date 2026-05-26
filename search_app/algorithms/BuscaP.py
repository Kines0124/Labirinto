"""
algorithms/BuscaP.py
===================
Classe contendo algoritmos de busca para grafos ponderados.
"""


from __future__       import annotations
from collections      import deque
from algorithms.NodeP import NodeP
from math             import sqrt, fabs
from typing           import Optional


# Tipos auxiliares para legibilidade
Node      = str                             # identificador de nó no grafo
GrafoAdj  = list[list[tuple[Node, float]]]  # lista de adjacência ponderada
Pesos     = dict[Node, float]               # heurística pré-calculada por nó
Caminho   = list[Node]
Resultado = Optional[tuple[Caminho, float]]


class buscaP(object):
# --------------------------------------------------------------------------
# SUCESSORES PARA GRAFO
# --------------------------------------------------------------------------
    def sucessores_grafo(self,
                         ind:   int,
                         grafo: GrafoAdj,
                         ordem: int,
                         ) -> list[tuple[Node, float]]:
        """Retorna a lista de sucessores (nó, custo) do nó de índice *ind*
        no grafo de adjacência, respeitando a ordem de iteração."""
        
        f: list[tuple[Node, float]] = []
        for suc in grafo[ind][::ordem]:
            f.append(suc)
        return f

# --------------------------------------------------------------------------
# SUCESSORES PARA GRID
# --------------------------------------------------------------------------
    def sucessores_grid(self,
                        st:   list[int],
                        nx:   int,
                        ny:   int,
                        mapa: list[list[int]],
                        ) -> list[list]:
        """Retorna os vizinhos válidos (direita, esquerda, abaixo, acima)
        de uma célula *st* em um grid, com os custos direcionais fixos."""

        f: list[list] = []
        x, y = st[0], st[1]
        # DIREITA
        if y+1<ny:
            if mapa[x][y+1]==0:
                suc = []
                suc.append(x)
                suc.append(y+1)
                custo = 5
                aux = []
                aux.append(suc)
                aux.append(custo)
                f.append(aux)
        # ESQUERDA
        if y-1>=0:
            if mapa[x][y-1]==0:
                suc = []
                suc.append(x)
                suc.append(y-1)
                custo = 7
                aux = []
                aux.append(suc)
                aux.append(custo)
                f.append(aux)
        # ABAIXO
        if x+1<nx:
            if mapa[x+1][y]==0:
                suc = []
                suc.append(x+1)
                suc.append(y)
                custo = 2
                aux = []
                aux.append(suc)
                aux.append(custo)
                f.append(aux)
        # ACIMA
        if x-1>=0:
            if mapa[x-1][y]==0:
                suc = []
                suc.append(x-1)
                suc.append(y)
                custo = 3
                aux = []
                aux.append(suc)
                aux.append(custo)
                f.append(aux)
        return f

# --------------------------------------------------------------------------
# INSERE NA LISTA MANTENDO-A ORDENADA
# --------------------------------------------------------------------------
    def inserir_ordenado(self,
                         lista: deque[NodeP],
                         no:    NodeP,
                         ) -> None:
        """Insere *no* na deque mantendo-a ordenada crescentemente por v1
        (custo f = g + h), usando inserção linear."""

        for i, n in enumerate(lista):
            if no.v1 < n.v1:
                lista.insert(i, no)
                break
        else:
            lista.append(no)

# --------------------------------------------------------------------------
# EXIBE O CAMINHO ENCONTRADO NA ÁRVORE DE BUSCA
# --------------------------------------------------------------------------
    def exibirCaminho(self, node: NodeP) -> Caminho:
        """Reconstrói o caminho do nó *node* até a raiz seguindo os
        ponteiros pai, retornando a lista de estados na ordem inversa."""

        caminho: Caminho = []
        while node is not None:
            caminho.append(node.estado)
            node = node.pai
        #caminho.reverse()
        return caminho

# --------------------------------------------------------------------------
# GERA H - GRAFO
# --------------------------------------------------------------------------
    def heuristica_grafo(self,
                         nos:    list[Node],
                         inicio: Node,
                         destino: Node,
                         ) -> float:
        """Placeholder de heurística para grafo genérico; deve ser
        sobrescrito ou substituído por uma heurística admissível real."""
        return

# --------------------------------------------------------------------------
# GERA H - GRID
# --------------------------------------------------------------------------
    def heuristica_grid(self,
                        p1: list[int],
                        p2: list[int],
                        ) -> float:
        """Heurística euclidiana ponderada para grid, levando em conta os
        custos direcionais assimétricos (cima/baixo ≠ esquerda/direita)."""

        if (p2[0]-p1[0])<0:
            c1 = 3
        else:
            c1 = 2
        if (p2[1]-p1[1])<0:
            c2 = 7
        else:
            c2 = 5
        h = sqrt(c1*(p1[0]-p2[0])*(p1[0]-p2[0]) + c2*(p1[1]-p2[1])*(p1[1]-p2[1]))
        #h = c1*fabs(p1[0]-p2[0]) + c2*fabs(p1[1]-p2[1])
        return h

# -----------------------------------------------------------------------------
# CUSTO UNIFORME - GRID
# -----------------------------------------------------------------------------
    def custo_uniforme_grid(self,
                            inicio: list[int],
                            fim:    list[int],
                            mapa:   list[list[int]],
                            nx:     int,
                            ny:     int,
                            ) -> Resultado:
        """Busca de custo uniforme (Dijkstra) em grid: expande sempre o nó
        de menor custo acumulado g, garantindo solução ótima."""

        # Origem igual a destino
        if inicio == fim:
            return [inicio], 0
        
        # Fila de prioridade baseada em deque + inserção ordenada
        lista: deque[NodeP] = deque()
        t_inicio = tuple(inicio)
        raiz = NodeP(None, t_inicio, 0, None, None, 0)
        lista.append(raiz)
    
        # Controle de nós visitados
        visitado: dict[tuple, NodeP] = {tuple(inicio): raiz}
        
        # loop de busca
        while lista:
            # remove o primeiro nó
            atual = lista.popleft()
            valor_atual: float = atual.v2
    
            # Chegou ao objetivo
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
    
            # Gera sucessores - grid
            filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
    
            for novo in filhos:
                # custo acumulado até o sucessor
                v2: float = valor_atual + novo[1]
                v1: float = v2
    
                # Não visitado ou custo melhor
                t_novo = tuple(novo[0])
                if (t_novo not in visitado) or (v2 < visitado[t_novo].v2):
                    filho = NodeP(atual, t_novo, v1, None, None, v2)
                    visitado[t_novo] = filho
                    self.inserir_ordenado(lista, filho)
        return None

# -----------------------------------------------------------------------------
# CUSTO UNIFORME - GRAFO
# -----------------------------------------------------------------------------
    def custo_uniforme_grafo(self,
                             inicio: Node,
                             fim:    Node,
                             nos:    list[Node],
                             grafo:  GrafoAdj,
                             ) -> Resultado:
        """Busca de custo uniforme (Dijkstra) em grafo: expande sempre o nó
        de menor custo acumulado g, garantindo solução ótima."""

        # Origem igual a destino
        if inicio == fim:
            return [inicio], 0
        
        # Fila de prioridade baseada em deque + inserção ordenada
        lista: deque[NodeP] = deque()
        raiz = NodeP(None, inicio, 0, None, None, 0)
        lista.append(raiz)
    
        # Controle de nós visitados
        visitado: dict[Node, NodeP] = {inicio: raiz}

        # loop de busca
        while lista:
            # remove o primeiro nó
            atual = lista.popleft()
            valor_atual: float = atual.v2
    
            # Chegou ao objetivo
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
    
            # Gera sucessores - grafo
            ind: int = nos.index(atual.estado)
            filhos = self.sucessores_grafo(ind, grafo, 1)
            
            for novo in filhos:
                # custo acumulado até o sucessor
                v2: float = valor_atual + novo[1]
                v1: float = v2
    
                # Não visitado ou custo melhor
                if (novo[0] not in visitado) or (v2 < visitado[novo[0]].v2):
                    filho = NodeP(atual, novo[0], v1, None, None, v2)
                    visitado[novo[0]] = filho
                    self.inserir_ordenado(lista, filho)
        return None

# -----------------------------------------------------------------------------
# GREEDY - GRID
# -----------------------------------------------------------------------------
    def greedy_grid(self,
                    inicio: list[int],
                    fim:    list[int],
                    mapa:   list[list[int]],
                    nx:     int,
                    ny:     int,
                    ) -> Resultado:
        """Busca gulosa em grid: ordena a fila apenas pela heurística h,
        sem considerar o custo acumulado g (não garante solução ótima)."""

        # Origem igual a destino
        if inicio == fim:
            return [inicio], 0
        
        # Fila de prioridade baseada em deque + inserção ordenada
        lista: deque[NodeP] = deque()
        t_inicio = tuple(inicio)
        raiz = NodeP(None, t_inicio, 0, None, None, 0)
        lista.append(raiz)
    
        # Controle de nós visitados
        visitado: dict[tuple, NodeP] = {tuple(inicio): raiz}
        
        # loop de busca
        while lista:
            # remove o primeiro nó
            atual = lista.popleft()
            valor_atual: float = atual.v2
    
            # Chegou ao objetivo
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
            
            # Gera sucessores
            filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
    
            for novo in filhos:
                # custo acumulado até o sucessor
                v2: float = valor_atual + novo[1]
                v1: float = self.heuristica_grid(novo[0], fim)
    
                # Não visitado ou custo melhor
                t_novo = tuple(novo[0])
                if (t_novo not in visitado) or (v2 < visitado[t_novo].v2):
                    filho = NodeP(atual, t_novo, v1, None, None, v2)
                    visitado[t_novo] = filho
                    self.inserir_ordenado(lista, filho)
        return None

# -----------------------------------------------------------------------------
# GREEDY - GRAFO
# -----------------------------------------------------------------------------
    def greedy_grafo(self,
                     inicio: Node,
                     fim:    Node,
                     nos:    list[Node],
                     grafo:  GrafoAdj,
                     pesos:  Pesos,
                     ) -> Resultado:
        """Busca gulosa em grafo: ordena a fila apenas pela heurística h
        pré-calculada, ignorando o custo acumulado g."""

        # Origem igual a destino
        if inicio == fim:
            return [inicio], 0
        
        # Fila de prioridade baseada em deque + inserção ordenada
        lista: deque[NodeP] = deque()
        raiz = NodeP(None, inicio, 0, None, None, 0)
        lista.append(raiz)
    
        # Controle de nós visitados
        visitado: dict[Node, NodeP] = {inicio: raiz}
        
        # loop de busca
        while lista:
            # remove o primeiro nó
            atual = lista.popleft()
            valor_atual: float = atual.v2
    
            # Chegou ao objetivo
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
    
            # Gera sucessores
            ind: int = nos.index(atual.estado)
            filhos = self.sucessores_grafo(ind, grafo, 1)
    
            for novo in filhos:
                # custo acumulado até o sucessor
                v2: float = valor_atual + novo[1]
                v1: float = pesos[novo[0]]
    
                # Não visitado ou custo melhor
                if (novo[0] not in visitado) or (v2 < visitado[novo[0]].v2):
                    filho = NodeP(atual, novo[0], v1, None, None, v2)
                    visitado[novo[0]] = filho
                    self.inserir_ordenado(lista, filho)
        return None

# -----------------------------------------------------------------------------
# A ESTRELA - GRID
# -----------------------------------------------------------------------------
    def a_estrela_grid(self,
                       inicio: list[int],
                       fim:    list[int],
                       mapa:   list[list[int]],
                       nx:     int,
                       ny:     int,
                       ) -> Resultado:
        """A* em grid: combina custo acumulado g com heurística euclidiana
        ponderada h para garantir solução ótima de forma eficiente."""

        # Origem igual a destino
        if inicio == fim:
            return [inicio], 0
        
        # Fila de prioridade baseada em deque + inserção ordenada
        lista: deque[NodeP] = deque()
        t_inicio = tuple(inicio)
        raiz = NodeP(None, t_inicio, 0, None, None, 0)
        lista.append(raiz)
    
        # Controle de nós visitados
        visitado: dict[tuple, NodeP] = {tuple(inicio): raiz}
        
        # loop de busca
        while lista:
            # remove o primeiro nó
            atual = lista.popleft()
            valor_atual: float = atual.v2
    
            # Chegou ao objetivo
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
            
            # Gera sucessores
            filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
    
            for novo in filhos:
                # custo acumulado até o sucessor
                v2: float = valor_atual + novo[1]
                v1: float = v2 + self.heuristica_grid(novo[0], fim)
    
                # Não visitado ou custo melhor
                t_novo = tuple(novo[0])
                if (t_novo not in visitado) or (v2 < visitado[t_novo].v2):
                    filho = NodeP(atual, t_novo, v1, None, None, v2)
                    visitado[t_novo] = filho
                    self.inserir_ordenado(lista, filho)
        return None

# -----------------------------------------------------------------------------
# A ESTRELA - GRAFO
# -----------------------------------------------------------------------------
    def a_estrela_grafo(self,
                        inicio: Node,
                        fim:    Node,
                        nos:    list[Node],
                        grafo:  GrafoAdj,
                        pesos:  Pesos,
                        ) -> Resultado:
        """A* em grafo: combina custo acumulado g com heurística h
        pré-calculada para encontrar o caminho ótimo eficientemente."""

        # Origem igual a destino
        if inicio == fim:
            return [inicio], 0
        
        # Fila de prioridade baseada em deque + inserção ordenada
        lista: deque[NodeP] = deque()
        raiz = NodeP(None, inicio, 0, None, None, 0)
        lista.append(raiz)
    
        # Controle de nós visitados
        visitado: dict[Node, NodeP] = {inicio: raiz}
        
        # loop de busca
        while lista:
            # remove o primeiro nó
            atual = lista.popleft()
            valor_atual: float = atual.v2
    
            # Chegou ao objetivo
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
    
            # Gera sucessores
            ind: int = nos.index(atual.estado)
            filhos = self.sucessores_grafo(ind, grafo, 1)
    
            for novo in filhos:
                # custo acumulado até o sucessor
                v2: float = valor_atual + novo[1]
                v1: float = v2 + pesos[novo[0]]
    
                # Não visitado ou custo melhor
                if (novo[0] not in visitado) or (v2 < visitado[novo[0]].v2):
                    filho = NodeP(atual, novo[0], v1, None, None, v2)
                    visitado[novo[0]] = filho
                    self.inserir_ordenado(lista, filho)
        return None

# -----------------------------------------------------------------------------
# AIA ESTRELA - GRID
# -----------------------------------------------------------------------------
    def aia_estrela_grid(self,
                         inicio: list[int],
                         fim:    list[int],
                         mapa:   list[list[int]],
                         nx:     int,
                         ny:     int,
                         ) -> Resultado:
        """AIA* (A* com aprofundamento iterativo) em grid: repete buscas
        A* com limite f crescente (mínimo dos excedentes) até encontrar
        o goal, mantendo consumo de memória linear."""

        # Origem igual a destino
        if inicio == fim:
            return [inicio], 0
        lim: float = self.heuristica_grid(inicio, fim)
        
        while True:
            # Fila de prioridade baseada em deque + inserção ordenada
            lista: deque[NodeP] = deque()
            t_inicio = tuple(inicio)
            raiz = NodeP(None, t_inicio, 0, None, None, 0)
            lista.append(raiz)
        
            # Controle de nós visitados
            visitado: dict[tuple, NodeP] = {tuple(inicio): raiz}
            
            # loop de busca
            novo_lim: list[float] = []
            while lista:
                # remove o primeiro nó
                atual = lista.popleft()
                valor_atual: float = atual.v2
        
                # Chegou ao objetivo
                if atual.estado == fim:
                    return self.exibirCaminho(atual), atual.v2
                
                # Gera sucessores
                filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
        
                for novo in filhos:
                    # custo acumulado até o sucessor
                    v2: float = valor_atual + novo[1]
                    v1: float = v2 + self.heuristica_grid(novo[0], fim)
                    
                    if v1 <= lim:
                        # Não visitado ou custo melhor
                        t_novo = tuple(novo[0])
                        if (t_novo not in visitado) or (v2 < visitado[t_novo].v2):
                            filho = NodeP(atual, t_novo, v1, None, None, v2)
                            visitado[t_novo] = filho
                            self.inserir_ordenado(lista, filho)
                    else:
                        novo_lim.append(v1)

            if not novo_lim:
                return None

            # Avança o limite para o menor f que excedeu o corte anterior
            lim = min(novo_lim)
            lista.clear()
            visitado.clear()
            novo_lim.clear()

# -----------------------------------------------------------------------------
# AIA ESTRELA - GRAFO
# -----------------------------------------------------------------------------
    def aia_estrela_grafo(self,
                          inicio: Node,
                          fim:    Node,
                          nos:    list[Node],
                          grafo:  GrafoAdj,
                          pesos:  Pesos,
                          ) -> Resultado:
        """AIA* (A* com aprofundamento iterativo) em grafo: repete buscas
        A* com limite f crescente (mínimo dos excedentes) até encontrar
        o goal, mantendo consumo de memória linear."""

        if inicio == fim:
            return [inicio], 0

        lim: float = pesos[inicio]

        while True:
            lista: deque[NodeP] = deque()
            raiz = NodeP(None, inicio, 0, None, None, 0)
            lista.append(raiz)
            visitado: dict[Node, NodeP] = {inicio: raiz}
            novo_lim: list[float] = []

            while lista:
                atual = lista.popleft()
                valor_atual: float = atual.v2

                # Chegou ao objetivo
                if atual.estado == fim:
                    return self.exibirCaminho(atual), atual.v2

                # Gera sucessores
                ind: int = nos.index(atual.estado)
                filhos = self.sucessores_grafo(ind, grafo, 1)

                for novo in filhos:
                    # custo acumulado até o sucessor
                    v2: float = valor_atual + novo[1]
                    v1: float = v2 + pesos[novo[0]]

                    if v1 <= lim:
                        # Não visitado ou custo melhor
                        if (novo[0] not in visitado) or (v2 < visitado[novo[0]].v2):
                            filho = NodeP(atual, novo[0], v1, None, None, v2)
                            visitado[novo[0]] = filho
                            self.inserir_ordenado(lista, filho)
                    else:
                        novo_lim.append(v1)

            if not novo_lim:
                return None

            # Avança o limite para o menor f que excedeu o corte anterior
            lim = min(novo_lim)

# -----------------------------------------------------------------------------
# A ESTRELA MULTI
# -----------------------------------------------------------------------------
    def a_estrela_multi(self,
                        inicio: Node,
                        fim:    list[Node],
                        nos:    list[Node],
                        grafo:  GrafoAdj,
                        ) -> Optional[tuple[Caminho, float]]:
        """A* multi-objetivo: encadeia buscas A* passando por múltiplos
        goals na ordem em que são encontrados, concatenando os subcaminhos."""
        
        # Fila de prioridade baseada em deque + inserção ordenada
        caminho: list[Caminho] = []
        while True:
            lista: deque[NodeP] = deque()
            raiz = NodeP(None, inicio, 0, None, None, 0)
            lista.append(raiz)
        
            # Controle de nós visitados
            visitado: dict[Node, NodeP] = {inicio: raiz}
            
            # loop de busca
            while lista:
                # remove o primeiro nó
                atual = lista.popleft()
                valor_atual: float = atual.v2
        
                # Chegou ao objetivo
                if atual.estado in fim:
                    caminho.append(self.exibirCaminho(atual))
                    inicio = atual.estado
                    fim.remove(atual.estado)
                    if len(fim) == 0:
                        res: Caminho = []
                        flag = True
                        for lista in caminho:
                            print(lista)
                            if flag:
                                for ponto in lista[::-1]:
                                    res.append(ponto)
                                flag = False
                            else:
                                lista = lista[::-1]
                                for i in range(1, len(lista)):
                                    res.append(lista[i])
                        return res[::-1], 0
                    break
        
                # Gera sucessores - grafo
                ind: int = nos.index(atual.estado)
                filhos = self.sucessores_grafo(ind, grafo, 1)
                
                for novo in filhos:
                    # custo acumulado até o sucessor
                    v2: float = valor_atual + novo[1]
                    v1: float = v2 + self.heuristica_grafo(nos, fim, novo[0])
        
                    # Não visitado ou custo melhor
                    if (novo[0] not in visitado) or (v2 < visitado[novo[0]].v2):
                        filho = NodeP(atual, novo[0], v1, None, None, v2)
                        visitado[novo[0]] = filho
                        self.inserir_ordenado(lista, filho)
        return None