"""
algorithms/Node.py
===================
A class for implementing nodes in unweighted graphs.
"""


class Node(object):

    def __init__(self, parent=None, state=None, v1=None,
                 previous=None,  next=None):
        self.parent    = parent
        self.state     = state
        self.v1        = v1
        self.previous  = previous
        self.next      = next

