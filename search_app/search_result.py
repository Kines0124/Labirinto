"""
search_result.py
================
Defines the default return type for all search algorithms.
"""

from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """Standardized result of a search."""
    path:           list[str] = field(default_factory=list)
    cost:           float     = 0.0
    depth:          int       = 0

    @property
    def found(self) -> bool:
        return len(self.path) > 0

    def to_dict(self) -> dict:
        """Compatibility with legacy code that expects a dictionary."""
        return {
            'path':           self.path,
            'cost':           self.cost,
            'depth':          self.depth,
        }