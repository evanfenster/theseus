from dataclasses import dataclass, field
from typing import Set

@dataclass
class Relationship:
    information: str
    document_source: int
    document_permissions: Set[int]
