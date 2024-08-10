from dataclasses import dataclass, field
from typing import Set, Dict, Any
from .relationship import Relationship

@dataclass
class Node:
    name: str
    facts: Dict[int, Set[str]] = field(default_factory=dict)
    documents: Set[int] = field(default_factory=set)
    edges: Dict['Node', Set[Relationship]] = field(default_factory=dict)

    def __init__(self, name: str):
        self.name = name
        self.facts = dict()
        self.documents = set()
        self.edges = dict()

    def add_document(self, document: int) -> None:
        self.documents.add(document)

    def add_fact(self, document: int, fact: str) -> None:
        if document not in self.facts:
            self.facts[document] = set()
        self.facts[document].add(fact)

    def add_relationship(self, target_node: 'Node', relationship: Relationship) -> None:
        if target_node not in self.edges:
            self.edges[target_node] = set()
        self.edges[target_node].add(relationship)

    def get_edge_weight(self, target_node: 'Node', permissions: Set[str]) -> int:
        # Returns the number of relationships in the edge to target_node that can be accessed based on permissions
        return sum(1 for relationship in self.edges[target_node] if relationship.document_permissions.intersection(permissions))
    
    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.name == other.name
