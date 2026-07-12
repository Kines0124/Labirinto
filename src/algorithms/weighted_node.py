"""
algorithms/Node.py
===================
A class for implementing nodes in weighted graphs.
"""


from algorithms.node import Node

class WeightedNode(Node):
    
    def __init__(self, parent=None, state=None, v1=None,
                 previous=None, next=None, v2=None):
        super().__init__(parent, state, v1, previous, next)
        self.v2 = v2
