"""
algorithms/BuscaNP.py
===================
Class containing search algorithms for unweighted graphs.
"""


from __future__      import annotations
from collections     import deque
from algorithms.Node import Node
from typing          import Optional


# Helper types for readability
NodeId    = str                    # node identifier in the graph
GraphAdj  = list[list[NodeId]]     # unweighted adjacency list
Path      = list                   # list of states (str or list[int])
Result    = Optional[Path]


class UnweightedSearch(object):

# --------------------------------------------------------------------------
# GRAPH SUCCESSORS
# --------------------------------------------------------------------------
    def graph_successors(self,
                         index: int,
                         graph: GraphAdj,
                         order: int,
                         ) -> list[NodeId]:
        """Returns the list of successors of the node at *index* in the
        adjacency graph, respecting the iteration order (1 = normal, -1 = reversed)."""

        result: list[NodeId] = []
        for successor in graph[index][::order]:
            result.append(successor)
        return result

# --------------------------------------------------------------------------
# DISPLAYS THE PATH FOUND IN THE SEARCH TREE (GRAPH and GRID)
# --------------------------------------------------------------------------
    def show_path(self, node: Node) -> Path:
        """Reconstructs the path from the root to *node* by following the
        parent pointers and returns the list of states in the correct order (start → end)."""

        path: Path = []
        while node is not None:
            path.append(node.state)
            node = node.parent
        path.reverse()
        return path

# --------------------------------------------------------------------------
# LOCATES NODES WITHIN THE QUEUE
# --------------------------------------------------------------------------
    def find_meeting_node(self,
                          value: object,
                          node_list: deque[Node],
                          ) -> Optional[Node]:
        """Scans *node_list* from back to front and returns the first node whose
        state equals *value*; used by the bidirectional search."""

        for node in reversed(node_list):
            if node.state == value:
                return node

# --------------------------------------------------------------------------
# DISPLAYS THE PATH FOUND IN THE SEARCH TREE - BIDIRECTIONAL (GRAPH/GRID)
# --------------------------------------------------------------------------
    def show_path_bidirectional(self,
                                meeting_value: object,
                                queue1:        deque[Node],
                                queue2:        deque[Node],
                                ) -> Path:
        """Concatenates the subpaths from both halves of the bidirectional
        search: origin → meeting point + meeting point → destination (reversed)."""

        # node from the start side
        meeting_node1 = self.find_meeting_node(meeting_value, queue1)
        # node from the goal side
        meeting_node2 = self.find_meeting_node(meeting_value, queue2)
        
        path1 = self.show_path(meeting_node1)
        path2 = self.show_path(meeting_node2)
    
        # Reverses the path
        path2 = list(reversed(path2[:-1]))
    
        return path1 + path2

# --------------------------------------------------------------------------
# BREADTH-FIRST SEARCH - GRAPH
# --------------------------------------------------------------------------
    def breadth_first_graph(self,
                            start: NodeId,
                            goal:  NodeId,
                            nodes: list[NodeId],
                            graph: GraphAdj,
                            ) -> Result:
        """BFS on graph: explores nodes layer by layer, guaranteeing the path
        with the fewest edges between *start* and *goal*."""

        # Finishes if start equals goal
        if start == goal:
            return [start]
        
        # List for the search tree - QUEUE
        queue: deque[Node] = deque()
    
        # Adds start as the root node of the search tree
        root = Node(None, start, 0, None, None)
        queue.append(root)
    
        # Marks start as visited
        visited: dict[NodeId, int] = {}
        visited[start] = 0
        
        # Runs the search
        while queue:
            # Removes the first from the QUEUE
            current = queue.popleft()
    
            # Generates successors from the graph
            index: int = nodes.index(current.state)
            children = self.graph_successors(index, graph, 1)
            for child in children:
                flag = True
                if child in visited:
                    if visited[child] <= current.v1 + 1:
                        flag = False
                if flag:
                    new_node = Node(current, child, current.v1 + 1, None, None)
                    queue.append(new_node)
                    visited[child] = current.v1 + 1
                    
                    # Checks if the goal was found
                    if child == goal:
                        return self.show_path(new_node)
        return None

# --------------------------------------------------------------------------
# DEPTH-FIRST SEARCH - GRAPH
# --------------------------------------------------------------------------
    def depth_first_graph(self,
                          start: NodeId,
                          goal:  NodeId,
                          nodes: list[NodeId],
                          graph: GraphAdj,
                          ) -> Result:
        """DFS on graph: explores the deepest branch before backtracking,
        using an explicit stack with visited-node tracking."""

        # Finishes if start equals goal
        if start == goal:
            return [start]
    
        # List for the search tree - STACK
        stack: deque[Node] = deque()
    
        # Adds start as the root node of the search tree
        root = Node(None, start, 0, None, None)
        stack.append(root)
    
        # Marks start as visited
        visited: dict[NodeId, int] = {}
        visited[start] = 0
        
        while stack:
            # Removes the last from the STACK
            current = stack.pop()
    
            # Generates successors from the graph
            index: int = nodes.index(current.state)
            children = self.graph_successors(index, graph, -1)
            
            for child in children:
                flag = True
                if child in visited:
                    if visited[child] <= current.v1 + 1:
                        flag = False
                if flag:
                    new_node = Node(current, child, current.v1 + 1, None, None)
                    stack.append(new_node)
                    visited[child] = current.v1 + 1
                    
                    # Checks if the goal was found - multi-goal
                    if child == goal:
                        return self.show_path(new_node)
        return None

# --------------------------------------------------------------------------
# DEPTH-LIMITED SEARCH - GRAPH
# --------------------------------------------------------------------------
    def depth_limited_graph(self,
                            start: NodeId,
                            goal:  NodeId,
                            nodes: list[NodeId],
                            graph: GraphAdj,
                            limit: int,
                            ) -> Result:
        """DFS with a depth limit on graph: does not expand nodes beyond
        *limit* levels, avoiding loops in deep cyclic graphs."""

        # Finishes if start equals goal
        if start == goal:
            return [start]
    
        # List for the search tree - STACK
        stack: deque[Node] = deque()
    
        # Adds start as the root node of the search tree
        root = Node(None, start, 0, None, None)
        stack.append(root)
    
        # Marks start as visited
        visited: dict[NodeId, int] = {}
        visited[start] = 0
        
        while stack:
            # Removes the last from the STACK
            current = stack.pop()
            
            if current.v1 < limit:
                # Generates successors from the graph
                index: int = nodes.index(current.state)
                children = self.graph_successors(index, graph, -1)
                
                for child in children:
                    flag = True
                    if child in visited:
                        if visited[child] <= current.v1 + 1:
                            flag = False
                    if flag:
                        new_node = Node(current, child, current.v1 + 1, None, None)
                        stack.append(new_node)
                        visited[child] = current.v1 + 1
                        
                        # Checks if the goal was found - multi-goal
                        if child == goal:
                            return self.show_path(new_node)
        return None

# --------------------------------------------------------------------------
# ITERATIVE DEEPENING SEARCH - GRAPH
# --------------------------------------------------------------------------
    def iterative_deepening_graph(self,
                                  start:     NodeId,
                                  goal:      NodeId,
                                  nodes:     list[NodeId],
                                  graph:     GraphAdj,
                                  max_limit: int,
                                  ) -> Result:
        """IDDFS on graph: repeats limited DFS with an increasing limit from 1 to
        *max_limit*, combining BFS's completeness with DFS's memory efficiency."""

        # Finishes if start equals goal
        if start == goal:
            return [start]
        
        for limit in range(1, max_limit):
            # List for the search tree - STACK
            stack: deque[Node] = deque()
        
            # Adds start as the root node of the search tree
            root = Node(None, start, 0, None, None)
            stack.append(root)
        
            # Marks start as visited
            visited: dict[NodeId, int] = {}
            visited[start] = 0
            
            while stack:
                # Removes the first from the STACK
                current = stack.pop()
                
                if current.v1 < limit:
                    # Generates successors from the graph
                    index: int = nodes.index(current.state)
                    children = self.graph_successors(index, graph, -1)
                    
                    for child in children:
                        flag = True
                        if child in visited:
                            if visited[child] <= current.v1 + 1:
                               flag = False
                        if flag:
                            new_node = Node(current, child, current.v1 + 1, None, None)
                            stack.append(new_node)
                            visited[child] = current.v1 + 1
                            
                            # Checks if the goal was found
                            if child == goal:
                                return self.show_path(new_node)
        return None

# --------------------------------------------------------------------------
# BIDIRECTIONAL SEARCH - GRAPH
# --------------------------------------------------------------------------
    def bidirectional_graph(self,
                            start: NodeId,
                            goal:  NodeId,
                            nodes: list[NodeId],
                            graph: GraphAdj,
                            ) -> Result:
        """Bidirectional BFS on graph: expands simultaneously from the
        origin and the destination, finishing when the frontiers meet."""

        if start == goal:
            return [start]

        # List for the search tree from the origin - QUEUE
        queue1: deque[Node] = deque()
        
        # List for the search tree from the destination - QUEUE
        queue2: deque[Node] = deque()
        
        # Adds start and goal as root nodes of the search tree
        root = Node(None, start, 0, None, None)
        queue1.append(root)
        
        root = Node(None, goal, 0, None, None)
        queue2.append(root)
    
        # Visited mapping state -> Node (to reconstruct the path)
        visited1: dict[NodeId, int] = {}
        visited1[start] = 0
        visited2: dict[NodeId, int] = {}
        visited2[goal] = 0
        level: int = 0

        while queue1 and queue2:
            # ****** Runs BREADTH-FIRST from the ORIGIN *******
            # Number of nodes at the current level
            level = len(queue1)
            for _ in range(level):
                # Removes the first from the QUEUE
                current = queue1.popleft()

                # Generates successors
                index: int = nodes.index(current.state)
                children = self.graph_successors(index, graph, 1)
                
                for child in children:
                    flag = True
                    if child in visited1:
                        if visited1[child] <= current.v1 + 1:
                            flag = False
                    if flag:
                        new_node = Node(current, child, current.v1 + 1, None, None)
                        queue1.append(new_node)
                        visited1[child] = current.v1 + 1

                        if child in visited2:
                            return self.show_path_bidirectional(child, queue1, queue2)
            
            # ****** Runs BREADTH-FIRST from the GOAL *******
            # Number of nodes at the current level
            level = len(queue2)
            for _ in range(level):
                # Removes the first from the QUEUE
                current = queue2.popleft()

                # Generates successors
                index = nodes.index(current.state)
                children = self.graph_successors(index, graph, 1)
                            
                for child in children:
                    flag = True
                    if child in visited2:
                        if visited2[child] <= current.v1 + 1:
                            flag = False
                    if flag:
                        new_node = Node(current, child, current.v1 + 1, None, None)
                        queue2.append(new_node)
                        visited2[child] = current.v1 + 1
                        
                        if child in visited1:
                            return self.show_path_bidirectional(child, queue1, queue2)
                        
        return None