"""
algorithms/BuscaP.py
===================
Class containing search algorithms for weighted graphs.
"""


from __future__                 import annotations
from collections                import deque
from algorithms.weighted_node   import WeightedNode
from math                       import sqrt, fabs
from typing                     import Optional


# Helper types for readability
NodeId    = str                               # node identifier in the graph
GraphAdj  = list[list[tuple[NodeId, float]]]  # weighted adjacency list
Weights   = dict[NodeId, float]               # pre-computed heuristic per node
Path      = list[NodeId]
Result    = Optional[tuple[Path, float]]


class WeightedSearch(object):
# --------------------------------------------------------------------------
# GRAPH SUCCESSORS
# --------------------------------------------------------------------------
    def graph_successors(self,
                         index: int,
                         graph: GraphAdj,
                         order: int,
                         ) -> list[tuple[NodeId, float]]:
        """Returns the list of (node, cost) successors of the node at *index*
        in the adjacency graph, respecting the iteration order."""
        
        result: list[tuple[NodeId, float]] = []
        for successor in graph[index][::order]:
            result.append(successor)
        return result

# --------------------------------------------------------------------------
# INSERTS INTO THE LIST KEEPING IT SORTED
# --------------------------------------------------------------------------
    def insert_sorted(self,
                      queue: deque[WeightedNode],
                      node:  WeightedNode,
                      ) -> None:
        """Inserts *node* into the deque keeping it sorted in ascending order
        by v1 (cost f = g + h), using linear insertion."""

        for i, other in enumerate(queue):
            if node.v1 < other.v1:
                queue.insert(i, node)
                break
        else:
            queue.append(node)

# --------------------------------------------------------------------------
# DISPLAYS THE PATH FOUND IN THE SEARCH TREE
# --------------------------------------------------------------------------
    def show_path(self, node: WeightedNode) -> Path:
        """Reconstructs the path from *node* back to the root by following
        the parent pointers, returning the list of states in reverse order."""

        path: Path = []
        while node is not None:
            path.append(node.state)
            node = node.parent
        #path.reverse()
        return path

# --------------------------------------------------------------------------
# GENERATES H - GRAPH
# --------------------------------------------------------------------------
    def graph_heuristic(self,
                        nodes: list[NodeId],
                        start: NodeId,
                        goal:  NodeId,
                        ) -> float:
        """Heuristic placeholder for a generic graph; should be overridden
        or replaced by a real admissible heuristic."""
        return

# -----------------------------------------------------------------------------
# UNIFORM COST - GRAPH
# -----------------------------------------------------------------------------
    def uniform_cost_graph(self,
                           start: NodeId,
                           goal:  NodeId,
                           nodes: list[NodeId],
                           graph: GraphAdj,
                           ) -> Result:
        """Uniform cost search on graph: always expands the node with the
        lowest accumulated cost g, guaranteeing an optimal solution."""

        # Origin equals destination
        if start == goal:
            return [start], 0
        
        # Priority queue based on deque + sorted insertion
        queue: deque[WeightedNode] = deque()
        root = WeightedNode(None, start, 0, None, None, 0)
        queue.append(root)
    
        # Tracking of visited nodes
        visited: dict[NodeId, WeightedNode] = {start: root}

        # search loop
        while queue:
            # removes the first node
            current = queue.popleft()
            current_value: float = current.v2
    
            # Reached the goal
            if current.state == goal:
                return self.show_path(current), current.v2
    
            # Generates successors - graph
            index: int = nodes.index(current.state)
            children = self.graph_successors(index, graph, 1)
            
            for child in children:
                # accumulated cost to the successor
                cost_so_far: float = current_value + child[1]
                priority: float = cost_so_far
    
                # Not visited or better cost
                if (child[0] not in visited) or (cost_so_far < visited[child[0]].v2):
                    new_node = WeightedNode(current, child[0], priority, None, None, cost_so_far)
                    visited[child[0]] = new_node
                    self.insert_sorted(queue, new_node)
        return None

# -----------------------------------------------------------------------------
# GREEDY - GRAPH
# -----------------------------------------------------------------------------
    def greedy_graph(self,
                     start:   NodeId,
                     goal:    NodeId,
                     nodes:   list[NodeId],
                     graph:   GraphAdj,
                     weights: Weights,
                     ) -> Result:
        """Greedy search on graph: sorts the queue only by the pre-computed
        heuristic h, ignoring the accumulated cost g."""

        # Origin equals destination
        if start == goal:
            return [start], 0
        
        # Priority queue based on deque + sorted insertion
        queue: deque[WeightedNode] = deque()
        root = WeightedNode(None, start, 0, None, None, 0)
        queue.append(root)
    
        # Tracking of visited nodes
        visited: dict[NodeId, WeightedNode] = {start: root}
        
        # search loop
        while queue:
            # removes the first node
            current = queue.popleft()
            current_value: float = current.v2
    
            # Reached the goal
            if current.state == goal:
                return self.show_path(current), current.v2
    
            # Generates successors
            index: int = nodes.index(current.state)
            children = self.graph_successors(index, graph, 1)
    
            for child in children:
                # accumulated cost to the successor
                cost_so_far: float = current_value + child[1]
                priority: float = weights[child[0]]
    
                # Not visited or better cost
                if (child[0] not in visited) or (cost_so_far < visited[child[0]].v2):
                    new_node = WeightedNode(current, child[0], priority, None, None, cost_so_far)
                    visited[child[0]] = new_node
                    self.insert_sorted(queue, new_node)
        return None

# -----------------------------------------------------------------------------
# A STAR - GRAPH
# -----------------------------------------------------------------------------
    def a_star_graph(self,
                     start:   NodeId,
                     goal:    NodeId,
                     nodes:   list[NodeId],
                     graph:   GraphAdj,
                     weights: Weights,
                     ) -> Result:
        """A* on graph: combines accumulated cost g with a pre-computed
        heuristic h to find the optimal path efficiently."""

        # Origin equals destination
        if start == goal:
            return [start], 0
        
        # Priority queue based on deque + sorted insertion
        queue: deque[WeightedNode] = deque()
        root = WeightedNode(None, start, 0, None, None, 0)
        queue.append(root)
    
        # Tracking of visited nodes
        visited: dict[NodeId, WeightedNode] = {start: root}
        
        # search loop
        while queue:
            # removes the first node
            current = queue.popleft()
            current_value: float = current.v2
    
            # Reached the goal
            if current.state == goal:
                return self.show_path(current), current.v2
    
            # Generates successors
            index: int = nodes.index(current.state)
            children = self.graph_successors(index, graph, 1)
    
            for child in children:
                # accumulated cost to the successor
                cost_so_far: float = current_value + child[1]
                priority: float = cost_so_far + weights[child[0]]
    
                # Not visited or better cost
                if (child[0] not in visited) or (cost_so_far < visited[child[0]].v2):
                    new_node = WeightedNode(current, child[0], priority, None, None, cost_so_far)
                    visited[child[0]] = new_node
                    self.insert_sorted(queue, new_node)
        return None

# -----------------------------------------------------------------------------
# IDA STAR - GRAPH
# -----------------------------------------------------------------------------
    def ida_star_graph(self,
                       start:   NodeId,
                       goal:    NodeId,
                       nodes:   list[NodeId],
                       graph:   GraphAdj,
                       weights: Weights,
                       ) -> Result:
        """IDA* (iterative-deepening A*) on graph: repeats A* searches with
        an increasing f limit (the minimum of the exceeding values) until
        the goal is found, keeping memory usage linear."""

        if start == goal:
            return [start], 0

        limit: float = weights[start]

        while True:
            queue: deque[WeightedNode] = deque()
            root = WeightedNode(None, start, 0, None, None, 0)
            queue.append(root)
            visited: dict[NodeId, WeightedNode] = {start: root}
            new_limits: list[float] = []

            while queue:
                current = queue.popleft()
                current_value: float = current.v2

                # Reached the goal
                if current.state == goal:
                    return self.show_path(current), current.v2

                # Generates successors
                index: int = nodes.index(current.state)
                children = self.graph_successors(index, graph, 1)

                for child in children:
                    # accumulated cost to the successor
                    cost_so_far: float = current_value + child[1]
                    priority: float = cost_so_far + weights[child[0]]

                    if priority <= limit:
                        # Not visited or better cost
                        if (child[0] not in visited) or (cost_so_far < visited[child[0]].v2):
                            new_node = WeightedNode(current, child[0], priority, None, None, cost_so_far)
                            visited[child[0]] = new_node
                            self.insert_sorted(queue, new_node)
                    else:
                        new_limits.append(priority)

            if not new_limits:
                return None

            # Advances the limit to the smallest f that exceeded the previous cutoff
            limit = min(new_limits)

# -----------------------------------------------------------------------------
# A STAR MULTI
# -----------------------------------------------------------------------------
    def a_star_multi(self,
                     start: NodeId,
                     goal:  list[NodeId],
                     nodes: list[NodeId],
                     graph: GraphAdj,
                     ) -> Optional[tuple[Path, float]]:
        """Multi-goal A*: chains A* searches through multiple goals in the
        order they are found, concatenating the sub-paths."""
        
        # Priority queue based on deque + sorted insertion
        path: list[Path] = []
        while True:
            queue: deque[WeightedNode] = deque()
            root = WeightedNode(None, start, 0, None, None, 0)
            queue.append(root)
        
            # Tracking of visited nodes
            visited: dict[NodeId, WeightedNode] = {start: root}
            
            # search loop
            while queue:
                # removes the first node
                current = queue.popleft()
                current_value: float = current.v2
        
                # Reached the goal
                if current.state in goal:
                    path.append(self.show_path(current))
                    start = current.state
                    goal.remove(current.state)
                    if len(goal) == 0:
                        result: Path = []
                        flag = True
                        for segment in path:
                            print(segment)
                            if flag:
                                for point in segment[::-1]:
                                    result.append(point)
                                flag = False
                            else:
                                segment = segment[::-1]
                                for i in range(1, len(segment)):
                                    result.append(segment[i])
                        return result[::-1], 0
                    break
        
                # Generates successors - graph
                index: int = nodes.index(current.state)
                children = self.graph_successors(index, graph, 1)
                
                for child in children:
                    # accumulated cost to the successor
                    cost_so_far: float = current_value + child[1]
                    priority: float = cost_so_far + self.graph_heuristic(nodes, goal, child[0])
        
                    # Not visited or better cost
                    if (child[0] not in visited) or (cost_so_far < visited[child[0]].v2):
                        new_node = WeightedNode(current, child[0], priority, None, None, cost_so_far)
                        visited[child[0]] = new_node
                        self.insert_sorted(queue, new_node)
        return None