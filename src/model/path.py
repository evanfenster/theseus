from dataclasses import dataclass, field
from typing import List, Union, Set
from .node import Node
from .relationship import Relationship

@dataclass
class Path:
    elements: List[Union[Node, Set[Relationship]]] = field(default_factory=list)

    def __init__(self):
        self.elements = []

    def add_node(self, node: Node) -> None:
        if not self.elements or isinstance(self.elements[-1], Set):
            self.elements.append(node)
        else:
            raise ValueError("Cannot add a node after another node. Add relationships in between.")

    def add_edge(self, relationships: Set[Relationship]) -> None:
        if self.elements and isinstance(self.elements[-1], Node):
            self.elements.append(relationships)
        else:
            raise ValueError("Cannot add edge to an empty path or after other edges. Add a node first.")
        
    def last_node(self) -> Node:
        if not self.elements:
            return None
        return self.elements[-1]
    
    def get_nodes(self) -> List[Node]:
        return [element for element in self.elements if isinstance(element, Node)]
    
    def pop(self, times: int = 1) -> None:
        for _ in range(times):
            if self.elements:
                self.elements.pop()
            else:
                break

    def copy(self) -> 'Path':
        new_path = Path()
        new_path.elements = self.elements.copy()
        return new_path

    def to_string(self, permissions: Set[int] = {-1}) -> str:
        result = []
        for i, element in enumerate(self.elements):
            if isinstance(element, Node):
                permitted_facts = [fact for doc_id, facts in element.facts.items() 
                                   for fact in facts 
                                   if -1 in permissions or doc_id in permissions]
                if permitted_facts:
                    result.append(f"{element.name}, Facts: {{{', '.join(permitted_facts)}}}")
                else:
                    result.append(f"{element.name}")
            else:  # Set of Relationships
                backward_rels = []
                forward_rels = []
                prev_node = next_node = None
                if i > 0 and isinstance(self.elements[i-1], Node):
                    prev_node = self.elements[i-1].name
                if i < len(self.elements) - 1 and isinstance(self.elements[i+1], Node):
                    next_node = self.elements[i+1].name
                
                for rel in element:
                    if -1 in permissions or rel.document_source in permissions:
                        (backward_rels if rel.backwards else forward_rels).append(rel.information)
                
                rel_strs = []
                if backward_rels:
                    rel_strs.append(f"from {next_node} to {prev_node}: {', '.join(backward_rels)}")
                if forward_rels:
                    rel_strs.append(f"from {prev_node} to {next_node}: {', '.join(forward_rels)}")
                
                if rel_strs:
                    result.append(f"[{', '.join(rel_strs)}]")
        
        return " -> ".join(result)

    def __repr__(self) -> str:
        return self.to_string()

