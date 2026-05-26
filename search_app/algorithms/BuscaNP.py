"""
algorithms/BuscaNP.py
===================
Classe contendo algoritmos de busca para grafos não ponderados.
"""


from __future__      import annotations
from collections     import deque
from algorithms.Node import Node
from typing          import Optional


# Tipos auxiliares para legibilidade
NodeId    = str                    # identificador de nó no grafo
GrafoAdj  = list[list[NodeId]]     # lista de adjacência sem pesos
Caminho   = list                   # lista de estados (str ou list[int])
Resultado = Optional[Caminho]


class buscaNP(object):

# --------------------------------------------------------------------------
# SUCESSORES PARA GRAFO
# --------------------------------------------------------------------------
    def sucessores_grafo(self,
                         ind:   int,
                         grafo: GrafoAdj,
                         ordem: int,
                         ) -> list[NodeId]:
        """Retorna a lista de sucessores do nó de índice *ind* no grafo de
        adjacência, respeitando a ordem de iteração (1 = normal, -1 = reversa)."""

        f: list[NodeId] = []
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
                        ) -> list[list[int]]:
        """Retorna os vizinhos livres (direita, esquerda, abaixo, acima) de
        uma célula *st* em um grid, na ordem reversa para uso com pilha."""

        f: list[list[int]] = []
        x, y = st[0], st[1]
        # DIREITA
        if y+1<ny:
            if mapa[x][y+1]==0:
                suc = []
                suc.append(x)
                suc.append(y+1)
                f.append(suc)
        # ESQUERDA
        if y-1>=0:
            if mapa[x][y-1]==0:
                suc = []
                suc.append(x)
                suc.append(y-1)
                f.append(suc)
        # ABAIXO
        if x+1<nx:
            if mapa[x+1][y]==0:
                suc = []
                suc.append(x+1)
                suc.append(y)
                f.append(suc)
        # ACIMA
        if x-1>=0:
            if mapa[x-1][y]==0:
                suc = []
                suc.append(x-1)
                suc.append(y)
                f.append(suc)
        return f[::-1]

# --------------------------------------------------------------------------
# EXIBE O CAMINHO ENCONTRADO NA ÁRVORE DE BUSCA (GRAFO e GRID)
# --------------------------------------------------------------------------
    def exibirCaminho(self, node: Node) -> Caminho:
        """Reconstrói o caminho da raiz até *node* seguindo os ponteiros
        pai e retorna a lista de estados na ordem correta (início → fim)."""

        caminho: Caminho = []
        while node is not None:
            caminho.append(node.estado)
            node = node.pai
        caminho.reverse()
        return caminho

# --------------------------------------------------------------------------
# LOCALIZA NÓS DENTRO DA FILA
# --------------------------------------------------------------------------
    def localiza_encontro(self,
                          valor: object,
                          lista: deque[Node],
                          ) -> Optional[Node]:
        """Varre *lista* de trás para frente e devolve o primeiro nó cujo
        estado seja igual a *valor*; usado pela busca bidirecional."""

        for no in reversed(lista):
            if no.estado == valor:
                return no

# --------------------------------------------------------------------------
# EXIBE O CAMINHO ENCONTRADO NA ÁRVORE DE BUSCA - BIDIRECIONAL (GRAFO/GRID)
# --------------------------------------------------------------------------
    def exibirCaminho_bid(self,
                          encontro: object,
                          fila1:    deque[Node],
                          fila2:    deque[Node],
                          ) -> Caminho:
        """Concatena os subcaminhos das duas metades da busca bidirecional:
        origem → ponto de encontro + ponto de encontro → destino (invertido)."""

        # nó do lado do início
        encontro1 = self.localiza_encontro(encontro, fila1)
        # nó do lado do objetivo
        encontro2 = self.localiza_encontro(encontro, fila2)
        
        caminho1 = self.exibirCaminho(encontro1)
        caminho2 = self.exibirCaminho(encontro2)
    
        # Inverte o caminho
        caminho2 = list(reversed(caminho2[:-1]))
    
        return caminho1 + caminho2

# --------------------------------------------------------------------------
# BUSCA EM AMPLITUDE - GRAFO
# --------------------------------------------------------------------------
    def amplitude_grafo(self,
                        inicio: NodeId,
                        fim:    NodeId,
                        nos:    list[NodeId],
                        grafo:  GrafoAdj,
                        ) -> Resultado:
        """BFS em grafo: explora nós camada a camada garantindo o caminho
        de menor número de arestas entre *inicio* e *fim*."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
        
        # Lista para árvore de busca - FILA
        fila: deque[Node] = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None, inicio, 0, None, None)
        fila.append(raiz)
    
        # Marca início como visitado
        visitado: dict[NodeId, int] = {}
        visitado[inicio] = 0
        
        # Executa a busca
        while fila:
            # Remove o primeiro da FILA
            atual = fila.popleft()
    
            # Gera sucessores a partir do grafo
            ind: int = nos.index(atual.estado)
            filhos = self.sucessores_grafo(ind, grafo, 1)
            for novo in filhos:
                flag = True
                if novo in visitado:
                    if visitado[novo] <= atual.v1 + 1:
                        flag = False
                if flag:
                    filho = Node(atual, novo, atual.v1 + 1, None, None)
                    fila.append(filho)
                    visitado[novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo
                    if novo == fim:
                        return self.exibirCaminho(filho)
        return None

# --------------------------------------------------------------------------
# BUSCA EM AMPLITUDE - GRID
# --------------------------------------------------------------------------
    def amplitude_grid(self,
                       inicio: list[int],
                       fim:    list[int],
                       nx:     int,
                       ny:     int,
                       mapa:   list[list[int]],
                       ) -> Resultado:
        """BFS em grid: explora células camada a camada garantindo o
        caminho de menor número de passos entre *inicio* e *fim*."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]

        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim    = tuple(fim)
        
        # Lista para árvore de busca - FILA
        fila: deque[Node] = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None, t_inicio, 0, None, None)
        fila.append(raiz)
    
        # Marca início como visitado
        visitado: dict[tuple, int] = {}
        visitado[t_inicio] = 0
        
        # Executa a busca
        while fila:
            # Remove o primeiro da FILA
            atual = fila.popleft()
    
            # Gera sucessores a partir do grid
            filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
    
            for novo in filhos:
                t_novo = tuple(novo)
                flag = True
                if t_novo in visitado:
                    if visitado[t_novo] <= atual.v1 + 1:
                        flag = False
                if flag:
                    filho = Node(atual, novo, atual.v1 + 1, None, None)
                    fila.append(filho)
                    visitado[t_novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo - multiobjetivo
                    if t_novo == t_fim:
                        return self.exibirCaminho(filho)
        return None

# --------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE - GRAFO
# --------------------------------------------------------------------------
    def profundidade_grafo(self,
                           inicio: NodeId,
                           fim:    NodeId,
                           nos:    list[NodeId],
                           grafo:  GrafoAdj,
                           ) -> Resultado:
        """DFS em grafo: explora o ramo mais profundo antes de retroceder,
        usando uma pilha explícita com controle de visitados."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
    
        # Lista para árvore de busca - PILHA
        pilha: deque[Node] = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None, inicio, 0, None, None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado: dict[NodeId, int] = {}
        visitado[inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
    
            # Gera sucessores a partir do grafo
            ind: int = nos.index(atual.estado)
            filhos = self.sucessores_grafo(ind, grafo, -1)
            
            for novo in filhos:
                flag = True
                if novo in visitado:
                    if visitado[novo] <= atual.v1 + 1:
                        flag = False
                if flag:
                    filho = Node(atual, novo, atual.v1 + 1, None, None)
                    pilha.append(filho)
                    visitado[novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo - multiobjetivo
                    if novo == fim:
                        return self.exibirCaminho(filho)
        return None

# --------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE - GRID
# --------------------------------------------------------------------------
    def profundidade_grid(self,
                          inicio: list[int],
                          fim:    list[int],
                          nx:     int,
                          ny:     int,
                          mapa:   list[list[int]],
                          ) -> Resultado:
        """DFS em grid: explora o ramo mais profundo antes de retroceder,
        usando uma pilha explícita com controle de visitados."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]

        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim    = tuple(fim)
        
        # Lista para árvore de busca - PILHA
        pilha: deque[Node] = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None, t_inicio, 0, None, None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado: dict[tuple, int] = {}
        visitado[t_inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
          
            # Gera sucessores a partir do grid
            filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
    
            for novo in filhos:
                t_novo = tuple(novo)
                flag = True
                if t_novo in visitado:
                    if visitado[t_novo] <= atual.v1 + 1:
                        flag = False
                if flag:
                    filho = Node(atual, novo, atual.v1 + 1, None, None)
                    pilha.append(filho)
                    visitado[t_novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo - multiobjetivo
                    if t_novo == t_fim:
                        return self.exibirCaminho(filho)
        return None

# --------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE LIMITADA - GRAFO
# --------------------------------------------------------------------------
    def prof_limitada_grafo(self,
                            inicio: NodeId,
                            fim:    NodeId,
                            nos:    list[NodeId],
                            grafo:  GrafoAdj,
                            lim:    int,
                            ) -> Resultado:
        """DFS com limite de profundidade em grafo: não expande nós além
        de *lim* níveis, evitando loops em grafos cíclicos profundos."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
    
        # Lista para árvore de busca - PILHA
        pilha: deque[Node] = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None, inicio, 0, None, None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado: dict[NodeId, int] = {}
        visitado[inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
            
            if atual.v1 < lim:
                # Gera sucessores a partir do grafo
                ind: int = nos.index(atual.estado)
                filhos = self.sucessores_grafo(ind, grafo, -1)
                
                for novo in filhos:
                    flag = True
                    if novo in visitado:
                        if visitado[novo] <= atual.v1 + 1:
                            flag = False
                    if flag:
                        filho = Node(atual, novo, atual.v1 + 1, None, None)
                        pilha.append(filho)
                        visitado[novo] = atual.v1 + 1
                        
                        # Verifica se encontrou o objetivo - multiobjetivo
                        if novo == fim:
                            return self.exibirCaminho(filho)
        return None

# --------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE LIMITADA - GRID
# --------------------------------------------------------------------------
    def prof_limitada_grid(self,
                           inicio: list[int],
                           fim:    list[int],
                           nx:     int,
                           ny:     int,
                           mapa:   list[list[int]],
                           lim:    int,
                           ) -> Resultado:
        """DFS com limite de profundidade em grid: não expande células além
        de *lim* níveis, evitando loops em espaços cíclicos."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
    
        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim    = tuple(fim)
        
        # Lista para árvore de busca - PILHA
        pilha: deque[Node] = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None, t_inicio, 0, None, None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado: dict[tuple, int] = {}
        visitado[t_inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
            
            if atual.v1 < lim:
                # Gera sucessores a partir do grid
                filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
        
                for novo in filhos:
                    t_novo = tuple(novo)
                    flag = True
                    if t_novo in visitado:
                        if visitado[t_novo] <= atual.v1 + 1:
                            flag = False
                    if flag:
                        filho = Node(atual, novo, atual.v1 + 1, None, None)
                        pilha.append(filho)
                        visitado[t_novo] = atual.v1 + 1
                        
                        # Verifica se encontrou o objetivo - multiobjetivo
                        if t_novo == t_fim:
                            return self.exibirCaminho(filho)
        return None

# --------------------------------------------------------------------------
# BUSCA EM APROFUNDAMENTO ITERATIVO - GRAFO
# --------------------------------------------------------------------------
    def aprof_iterativo_grafo(self,
                              inicio:   NodeId,
                              fim:      NodeId,
                              nos:      list[NodeId],
                              grafo:    GrafoAdj,
                              lim_max:  int,
                              ) -> Resultado:
        """IDDFS em grafo: repete DFS limitada com limite crescente de 1 até
        *lim_max*, combinando completude do BFS com memória do DFS."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
        
        for lim in range(1, lim_max):
            # Lista para árvore de busca - PILHA
            pilha: deque[Node] = deque()
        
            # Inclui início como nó raíz da árvore de busca
            raiz = Node(None, inicio, 0, None, None)
            pilha.append(raiz)
        
            # Marca início como visitado
            visitado: dict[NodeId, int] = {}
            visitado[inicio] = 0
            
            while pilha:
                # Remove o primeiro da PILHA
                atual = pilha.pop()
                
                if atual.v1 < lim:
                    # Gera sucessores a partir do grafo
                    ind: int = nos.index(atual.estado)
                    filhos = self.sucessores_grafo(ind, grafo, -1)
                    
                    for novo in filhos:
                        flag = True
                        if novo in visitado:
                            if visitado[novo] <= atual.v1 + 1:
                               flag = False
                        if flag:
                            filho = Node(atual, novo, atual.v1 + 1, None, None)
                            pilha.append(filho)
                            visitado[novo] = atual.v1 + 1
                            
                            # Verifica se encontrou o objetivo
                            if novo == fim:
                                return self.exibirCaminho(filho)
        return None

# --------------------------------------------------------------------------
# BUSCA EM APROFUNDAMENTO ITERATIVO - GRID
# --------------------------------------------------------------------------
    def aprof_iterativo_grid(self,
                             inicio:  list[int],
                             fim:     list[int],
                             nx:      int,
                             ny:      int,
                             mapa:    list[list[int]],
                             lim_max: int,
                             ) -> Resultado:
        """IDDFS em grid: repete DFS limitada com limite crescente de 1 até
        *lim_max*, combinando completude do BFS com memória do DFS."""

        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
        
        for lim in range(1, lim_max):
            # GRID: transforma em tupla
            t_inicio = tuple(inicio)
            t_fim    = tuple(fim)
            
            # Lista para árvore de busca - FILA
            pilha: deque[Node] = deque()
        
            # Inclui início como nó raíz da árvore de busca
            raiz = Node(None, t_inicio, 0, None, None)
            pilha.append(raiz)
        
            # Marca início como visitado
            visitado: dict[tuple, int] = {}
            visitado[t_inicio] = 0
            
            while pilha:
                # Remove o primeiro da FILA
                atual = pilha.pop()
                
                if atual.v1 < lim:
                    # Gera sucessores a partir do grid
                    filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)
            
                    for novo in filhos:
                        t_novo = tuple(novo)
                        flag = True
                        if t_novo in visitado:
                            if visitado[t_novo] <= atual.v1 + 1:
                                flag = False
                        if flag:
                            filho = Node(atual, novo, atual.v1 + 1, None, None)
                            pilha.append(filho)
                            visitado[t_novo] = atual.v1 + 1
                            
                            # Verifica se encontrou o objetivo
                            if t_novo == t_fim:
                                return self.exibirCaminho(filho)
            visitado.clear()
            pilha.clear()
        return None

# --------------------------------------------------------------------------
# BUSCA BIDIRECIONAL - GRAFO
# --------------------------------------------------------------------------
    def bidirecional_grafo(self,
                           inicio: NodeId,
                           fim:    NodeId,
                           nos:    list[NodeId],
                           grafo:  GrafoAdj,
                           ) -> Resultado:
        """BFS bidirecional em grafo: expande simultaneamente a partir da
        origem e do destino, terminando ao as fronteiras se encontrarem."""

        if inicio == fim:
            return [inicio]

        # Lista para árvore de busca a partir da origem - FILA
        fila1: deque[Node] = deque()
        
        # Lista para árvore de busca a partir do destino - FILA
        fila2: deque[Node] = deque()
        
        # Inclui início e fim como nó raíz da árvore de busca
        raiz = Node(None, inicio, 0, None, None)
        fila1.append(raiz)
        
        raiz = Node(None, fim, 0, None, None)
        fila2.append(raiz)
    
        # Visitados mapeando estado -> Node (para reconstruir o caminho)
        visitado1: dict[NodeId, int] = {}
        visitado1[inicio] = 0
        visitado2: dict[NodeId, int] = {}
        visitado2[fim] = 0
        nivel: int = 0

        while fila1 and fila2:
            # ****** Executa AMPLITUDE a partir da ORIGEM *******
            # Quantidade de nós no nível atual
            nivel = len(fila1)
            for _ in range(nivel):
                # Remove o primeiro da FILA
                atual = fila1.popleft()

                # Gera sucessores
                ind: int = nos.index(atual.estado)
                filhos = self.sucessores_grafo(ind, grafo, 1)
                
                for novo in filhos:
                    flag = True
                    if novo in visitado1:
                        if visitado1[novo] <= atual.v1 + 1:
                            flag = False
                    if flag:
                        filho = Node(atual, novo, atual.v1 + 1, None, None)
                        fila1.append(filho)
                        visitado1[novo] = atual.v1 + 1

                        if novo in visitado2:
                            return self.exibirCaminho_bid(novo, fila1, fila2)
            
            # ****** Executa AMPLITUDE a partir do OBJETIVO *******
            # Quantidade de nós no nível atual
            nivel = len(fila2)
            for _ in range(nivel):
                # Remove o primeiro da FILA
                atual = fila2.popleft()

                # Gera sucessores
                ind = nos.index(atual.estado)
                filhos = self.sucessores_grafo(ind, grafo, 1)
                            
                for novo in filhos:
                    flag = True
                    if novo in visitado2:
                        if visitado2[novo] <= atual.v1 + 1:
                            flag = False
                    if flag:
                        filho = Node(atual, novo, atual.v1 + 1, None, None)
                        fila2.append(filho)
                        visitado2[novo] = atual.v1 + 1
                        
                        if novo in visitado1:
                            return self.exibirCaminho_bid(novo, fila1, fila2)
                        
        return None

# --------------------------------------------------------------------------
# BUSCA BIDIRECIONAL - GRID
# --------------------------------------------------------------------------
    def bidirecional_grid(self,
                          inicio: list[int],
                          fim:    list[int],
                          nx:     int,
                          ny:     int,
                          mapa:   list[list[int]],
                          ) -> Resultado:
        """BFS bidirecional em grid: expande simultaneamente a partir da
        origem e do destino, terminando ao as fronteiras se encontrarem."""

        if inicio == fim:
            return [inicio]
        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim    = tuple(fim)

        # Lista para árvore de busca a partir da origem - FILA
        fila1: deque[Node] = deque()
        
        # Lista para árvore de busca a partir do destino - FILA
        fila2: deque[Node] = deque()
        
        # Inclui início e fim como nó raíz da árvore de busca
        raiz = Node(None, t_inicio, 0, None, None)
        fila1.append(raiz)
        raiz = Node(None, t_fim, 0, None, None)
        fila2.append(raiz)
    
        # Visitados mapeando estado -> Node (para reconstruir o caminho)
        visitado1: dict[tuple, int] = {}
        visitado1[t_inicio] = 0
        visitado2: dict[tuple, int] = {}
        visitado2[t_fim] = 0
        nivel: int = 0

        while fila1 and fila2:
            # ****** Executa AMPLITUDE a partir da ORIGEM *******
            # Quantidade de nós no nível atual
            nivel = len(fila1)
            for _ in range(nivel):
                # Remove o primeiro da FILA
                atual = fila1.popleft()
                
                # Gera sucessores a partir do grid
                filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)

                for novo in filhos:
                    t_novo = tuple(novo)
                    flag = True
                    if t_novo in visitado1:
                        if visitado1[t_novo] <= atual.v1 + 1:
                            flag = False
                    if flag:
                        filho = Node(atual, novo, atual.v1 + 1, None, None)
                        fila1.append(filho)
                        visitado1[t_novo] = atual.v1 + 1

                        # Encontrou encontro com a outra AMPLITUDE
                        if t_novo in visitado2:
                            return self.exibirCaminho_bid(novo, fila1, fila2)
            
            # ****** Executa AMPLITUDE a partir do OBJETIVO *******
            # Quantidade de nós no nível atual
            nivel = len(fila2)
            for _ in range(nivel):
                # Remove o primeiro da FILA
                atual = fila2.popleft()
                
                # Gera sucessores a partir do grid
                filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)

                for novo in filhos:
                    t_novo = tuple(novo)
                    flag = True
                    if t_novo in visitado2:
                        if visitado2[t_novo] <= atual.v1 + 1:
                            flag = False
                    if flag:
                        filho = Node(atual, novo, atual.v1 + 1, None, None)
                        fila2.append(filho)
                        visitado2[t_novo] = atual.v1 + 1

                        # Encontrou encontro com a outra AMPLITUDE
                        if t_novo in visitado1:
                            return self.exibirCaminho_bid(novo, fila1, fila2)
        return None