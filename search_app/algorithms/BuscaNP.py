from collections import deque
from algorithms.Node import Node

class buscaNP(object):
#--------------------------------------------------------------------------
# SUCESSORES PARA GRAFO
#--------------------------------------------------------------------------
    def sucessores_grafo(self,ind,grafo,ordem):
        
        f = []
        for suc in grafo[ind][::ordem]:
            f.append(suc)
        return f
#--------------------------------------------------------------------------
# SUCESSORES PARA GRID
#--------------------------------------------------------------------------
    def sucessores_grid(self,st,nx,ny,mapa):
        f = []
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
#--------------------------------------------------------------------------    
# EXIBE O CAMINHO ENCONTRADO NA ÁRVORE DE BUSCA (GRAFO e GRID)
#--------------------------------------------------------------------------    
    def exibirCaminho(self,node):
        caminho = []
        while node is not None:
            caminho.append(node.estado)
            node = node.pai
        caminho.reverse()
        return caminho
#--------------------------------------------------------------------------    
# LOCALIZA NÓS DENTRO DA FILA
#--------------------------------------------------------------------------
    def localiza_encontro(self,valor,lista):
        for no in reversed(lista):
            if no.estado==valor:
                return no
#--------------------------------------------------------------------------    
# EXIBE O CAMINHO ENCONTRADO NA ÁRVORE DE BUSCA - BIDIRECIONAL (GRAFO/GRID)
#--------------------------------------------------------------------------
    def exibirCaminho_bid(self,encontro,fila1,fila2):
        # nó do lado do início
        encontro1 = self.localiza_encontro(encontro,fila1)  
        # nó do lado do objetivo
        encontro2 = self.localiza_encontro(encontro,fila2)
        
        caminho1 = self.exibirCaminho(encontro1)
        caminho2 = self.exibirCaminho(encontro2)
    
        # Inverte o caminho
        caminho2 = list(reversed(caminho2[:-1]))
    
        return caminho1 + caminho2
#--------------------------------------------------------------------------
# BUSCA EM AMPLITUDE - GRAFO
#--------------------------------------------------------------------------
    def amplitude_grafo(self,inicio,fim,nos,grafo):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
        
        # Lista para árvore de busca - FILA
        fila = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None,inicio,0,None,None)
        fila.append(raiz)
    
        # Marca início como visitado
        visitado = {}
        visitado[inicio] = 0
        
        # Executa a busca
        while fila:
            # Remove o primeiro da FILA
            atual = fila.popleft()
    
            # Gera sucessores a partir do grafo
            ind = nos.index(atual.estado)
            filhos = self.sucessores_grafo(ind,grafo,1)
            for novo in filhos:
                flag = True
                if novo in visitado:
                    if visitado[novo]<=atual.v1+1:
                        flag = False
                if flag:
                    filho = Node(atual,novo,atual.v1 + 1,None,None)
                    fila.append(filho)
                    visitado[novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo
                    if novo == fim:
                        return self.exibirCaminho(filho)
        return None
#--------------------------------------------------------------------------
# BUSCA EM AMPLITUDE - GRID
#--------------------------------------------------------------------------
    def amplitude_grid(self,inicio,fim,nx,ny,mapa):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]

        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim = tuple(fim)
        
        # Lista para árvore de busca - FILA
        fila = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None,t_inicio,0,None,None)
        fila.append(raiz)
    
        # Marca início como visitado
        visitado = {}
        visitado[t_inicio] = 0
        
        # Executa a busca
        while fila:
            # Remove o primeiro da FILA
            atual = fila.popleft()
    
            # Gera sucessores a partir do grid
            filhos = self.sucessores_grid(atual.estado,nx,ny,mapa)
    
            for novo in filhos:
                t_novo = tuple(novo)
                flag = True
                if t_novo in visitado:
                    if visitado[t_novo]<=atual.v1+1:
                        flag = False
                if flag:
                    filho = Node(atual,novo,atual.v1 + 1,None,None)
                    fila.append(filho)
                    visitado[t_novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo - multiobjetivo
                    if t_novo == t_fim:
                        return self.exibirCaminho(filho)                            
        return None
#--------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE - GRAFO
#--------------------------------------------------------------------------
    def profundidade_grafo(self, inicio, fim, nos, grafo):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
    
        # Lista para árvore de busca - PILHA
        pilha = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None,inicio,0,None,None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado = {}
        visitado[inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
    
            # Gera sucessores a partir do grafo
            ind = nos.index(atual.estado)
            filhos = self.sucessores_grafo(ind,grafo,-1)
            
            for novo in filhos:
                flag = True
                if novo in visitado:
                    if visitado[novo]<=atual.v1+1:
                        flag = False
                if flag:
                    filho = Node(atual,novo,atual.v1 + 1,None,None)
                    pilha.append(filho)
                    visitado[novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo - multiobjetivo
                    if novo == fim:
                        return self.exibirCaminho(filho)
        return None
#--------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE - GRID
#--------------------------------------------------------------------------
    def profundidade_grid(self,inicio,fim,nx,ny,mapa):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]

        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim = tuple(fim)
        
        # Lista para árvore de busca - PILHA
        pilha = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None,t_inicio,0,None,None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado = {}
        visitado[t_inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
          
            # Gera sucessores a partir do grid
            filhos = self.sucessores_grid(atual.estado,nx,ny,mapa) # grid
    
            for novo in filhos:
                t_novo = tuple(novo)
                flag = True
                if t_novo in visitado:
                    if visitado[t_novo]<=atual.v1+1:
                        flag = False
                if flag:
                    filho = Node(atual,novo,atual.v1 + 1,None,None)
                    pilha.append(filho)
                    visitado[t_novo] = atual.v1 + 1
                    
                    # Verifica se encontrou o objetivo - multiobjetivo
                    if t_novo == t_fim:
                        return self.exibirCaminho(filho)
        return None
#--------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE LIMITADA - GRAFO
#--------------------------------------------------------------------------
    def prof_limitada_grafo(self,inicio,fim,nos,grafo,lim):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
    
        # Lista para árvore de busca - PILHA
        pilha = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None,inicio,0,None,None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado = {}
        visitado[inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
            
            if atual.v1<lim:
                # Gera sucessores a partir do grafo
                ind = nos.index(atual.estado)
                filhos = self.sucessores_grafo(ind,grafo,-1)
                
                for novo in filhos:
                    flag = True
                    if novo in visitado:
                        if visitado[novo]<=atual.v1+1:
                            flag = False
                    if flag:
                        filho = Node(atual,novo,atual.v1 + 1,None,None)
                        pilha.append(filho)
                        visitado[novo] = atual.v1 + 1
                        
                        # Verifica se encontrou o objetivo - multiobjetivo
                        if novo == fim:
                            return self.exibirCaminho(filho)
        return None
#--------------------------------------------------------------------------
# BUSCA EM PROFUNDIDADE LIMITADA - GRID
#--------------------------------------------------------------------------
    def prof_limitada_grid(self,inicio,fim,nx,ny,mapa,lim):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
    
        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim = tuple(fim)
        
        # Lista para árvore de busca - PILHA
        pilha = deque()
    
        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None,t_inicio,0,None,None)
        pilha.append(raiz)
    
        # Marca início como visitado
        visitado = {}
        visitado[t_inicio] = 0
        
        while pilha:
            # Remove o último da PILHA
            atual = pilha.pop()
            
            if atual.v1<lim:
                # Gera sucessores a partir do grid
                filhos = self.sucessores_grid(atual.estado,nx,ny,mapa)
        
                for novo in filhos:
                    t_novo = tuple(novo)
                    flag = True
                    if t_novo in visitado:
                        if visitado[t_novo]<=atual.v1+1:
                            flag = False
                    if flag:
                        filho = Node(atual,novo,atual.v1 + 1,None,None)
                        pilha.append(filho)
                        visitado[t_novo] = atual.v1 + 1
                        
                        # Verifica se encontrou o objetivo - multiobjetivo
                        if t_novo == t_fim:
                            return self.exibirCaminho(filho)
        return None
#--------------------------------------------------------------------------
# BUSCA EM APROFUNDAMENTO ITERATIVO - GRAFO
#--------------------------------------------------------------------------
    def aprof_iterativo_grafo(self,inicio,fim,nos,grafo,lim_max):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
        
        for lim in range(1,lim_max):    
            # Lista para árvore de busca - PILHA
            pilha = deque()
        
            # Inclui início como nó raíz da árvore de busca
            raiz = Node(None,inicio,0,None,None)
            pilha.append(raiz)
        
            # Marca início como visitado
            visitado = {}
            visitado[inicio] = 0
            
            while pilha:
                # Remove o primeiro da PILHA
                atual = pilha.pop()
                
                if atual.v1<lim:
                    # Gera sucessores a partir do grafo
                    ind = nos.index(atual.estado)
                    filhos = self.sucessores_grafo(ind,grafo,-1)
                    
                    for novo in filhos:
                        flag = True
                        if novo in visitado:
                            if visitado[novo]<=atual.v1+1:
                               flag = False
                        if flag:
                            filho = Node(atual,novo,atual.v1 + 1,None,None)
                            pilha.append(filho)
                            visitado[novo] = atual.v1 + 1
                            
                            # Verifica se encontrou o objetivo
                            if novo == fim:
                                return self.exibirCaminho(filho)
        return None
#--------------------------------------------------------------------------
# BUSCA EM APROFUNDAMENTO ITERATIVO - grid
#--------------------------------------------------------------------------
    def aprof_iterativo_grid(self,inicio,fim,nx,ny,mapa,lim_max):
        # Finaliza se início for igual a objetivo
        if inicio == fim:
            return [inicio]
        
        for lim in range(1,lim_max):   
            # GRID: transforma em tupla
            t_inicio = tuple(inicio)
            t_fim = tuple(fim)
            
            # Lista para árvore de busca - FILA
            pilha = deque()
        
            # Inclui início como nó raíz da árvore de busca
            raiz = Node(None,t_inicio,0,None,None)
            pilha.append(raiz)
        
            # Marca início como visitado
            visitado = {}
            visitado[t_inicio] = 0
            
            while pilha:
                # Remove o primeiro da FILA
                atual = pilha.pop()
                
                if atual.v1<lim:
                    # Gera sucessores a partir do grid
                    filhos = self.sucessores_grid(atual.estado,nx,ny,mapa)
            
                    for novo in filhos:
                        t_novo = tuple(novo)
                        flag = True
                        if t_novo in visitado:
                            if visitado[t_novo]<=atual.v1+1:
                                flag = False
                        if flag:
                            filho = Node(atual,novo,atual.v1 + 1,None,None)
                            pilha.append(filho)
                            visitado[t_novo] = atual.v1 + 1
                            
                            # Verifica se encontrou o objetivo
                            if t_novo == t_fim:
                                return self.exibirCaminho(filho)
            visitado.clear()
            pilha.clear()
        return None
#--------------------------------------------------------------------------
# BUSCA BIDIRECIONAL - GRAFO
#--------------------------------------------------------------------------
    def bidirecional_grafo(self,inicio,fim,nos,grafo):
        if inicio == fim:
            return [inicio]

        # Lista para árvore de busca a partir da origem - FILA
        fila1 = deque()
        
        # Lista para árvore de busca a partir do destino - FILA
        fila2 = deque()
        
        # Inclui início e fim como nó raíz da árvore de busca
        raiz = Node(None,inicio,0,None,None)
        fila1.append(raiz)
        
        raiz = Node(None,fim,0,None,None)
        fila2.append(raiz)
    
        # Visitados mapeando estado -> Node (para reconstruir o caminho)
        visitado1 = {}
        visitado1[inicio] = 0
        visitado2 = {}
        visitado2[fim] = 0        
        nivel = 0
        while fila1 and fila2:
            # ****** Executa AMPLITUDE a partir da ORIGEM *******
            # Quantidade de nós no nível atual
            nivel = len(fila1)  
            for _ in range(nivel):
                # Remove o primeiro da FILA
                atual = fila1.popleft()

                # Gera sucessores
                ind = nos.index(atual.estado)
                filhos = self.sucessores_grafo(ind, grafo, 1)
                
                for novo in filhos:
                    flag = True
                    if novo in visitado1:
                        if visitado1[novo]<=atual.v1+1:
                            flag = False
                    if flag:
                        filho = Node(atual,novo,atual.v1 + 1,None,None)
                        fila1.append(filho)
                        visitado1[novo] = atual.v1 + 1

                        if novo in visitado2:
                            return self.exibirCaminho_bid(novo,fila1,fila2)
            
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
                        if visitado2[novo]<=atual.v1+1:
                            flag = False
                    if flag:
                        filho = Node(atual,novo,atual.v1 + 1,None,None)
                        fila2.append(filho)
                        visitado2[novo] = atual.v1 + 1
                        
                        if novo in visitado1:
                            return self.exibirCaminho_bid(novo,fila1,fila2)
                        
        return None
#--------------------------------------------------------------------------
# BUSCA BIDIRECIONAL - GRID
#--------------------------------------------------------------------------
    def bidirecional_grid(self,inicio,fim,nx,ny,mapa):
        if inicio == fim:
            return [inicio]
        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim = tuple(fim)

        # Lista para árvore de busca a partir da origem - FILA
        fila1 = deque()
        
        # Lista para árvore de busca a partir do destino - FILA
        fila2 = deque()
        
        # Inclui início e fim como nó raíz da árvore de busca
        raiz = Node(None,t_inicio,0,None,None)
        fila1.append(raiz)
        raiz = Node(None,t_fim,0,None,None)
        fila2.append(raiz)
    
        # Visitados mapeando estado -> Node (para reconstruir o caminho)
        visitado1 = {}
        visitado1[t_inicio] = 0
        visitado2 = {}
        visitado2[t_fim] = 0
        # print(visitado1,visitado2)
        
        nivel = 0
        while fila1 and fila2:
            # ****** Executa AMPLITUDE a partir da ORIGEM *******
            # Quantidade de nós no nível atual
            nivel = len(fila1)  
            for _ in range(nivel):
                # Remove o primeiro da FILA
                atual = fila1.popleft()
                
                # Gera sucessores a partir do grid
                filhos = self.sucessores_grid(atual.estado,nx,ny,mapa) # grid

                for novo in filhos:
                    t_novo = tuple(novo)
                    flag = True
                    if t_novo in visitado1:
                        if visitado1[t_novo]<=atual.v1+1:
                            flag = False
                    if flag:
                        filho = Node(atual,novo,atual.v1 + 1,None,None)
                        fila1.append(filho)
                        visitado1[t_novo] = atual.v1 + 1

                        # Encontrou encontro com a outra AMPLITUDE
                        if t_novo in visitado2:
                            return self.exibirCaminho_bid(novo,fila1,fila2)
            
            # ****** Executa AMPLITUDE a partir do OBJETIVO *******
            # Quantidade de nós no nível atual
            nivel = len(fila2)  
            for _ in range(nivel):
                # Remove o primeiro da FILA
                atual = fila2.popleft()
                
                # Gera sucessores a partir do grid
                filhos = self.sucessores_grid(atual.estado,nx,ny,mapa)

                for novo in filhos:
                    t_novo = tuple(novo)
                    flag = True
                    if t_novo in visitado2:
                        if visitado2[t_novo]<=atual.v1+1:
                            flag = False
                    if flag:
                        filho = Node(atual,novo,atual.v1 + 1,None,None)
                        fila2.append(filho)
                        visitado2[t_novo] = atual.v1 + 1

                        # Encontrou encontro com a outra AMPLITUDE
                        if t_novo in visitado1:
                            return self.exibirCaminho_bid(novo,fila1,fila2)
        return None