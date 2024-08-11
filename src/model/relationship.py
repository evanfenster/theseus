from dataclasses import dataclass, field
from typing import Set

@dataclass
class Relationship:
    information: str
    document_source: int
    backwards: bool

    def __init__(self, information: str, document_source: int, backwards: bool):
        self.information = information
        self.document_source = document_source
        self.backwards = backwards

    def __hash__(self) -> int:
        return hash((self.information, self.document_source))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Relationship):
            return NotImplemented
        return (self.information == other.information and
                self.document_source == other.document_source)

    def __str__(self) -> str:
        return f"Relationship(information='{self.information}', source={self.document_source})"

    def __repr__(self) -> str:
        return self.__str__()

    def add_permission(self, permission: int) -> None:
        self.document_permissions.add(permission)

    def remove_permission(self, permission: int) -> None:
        self.document_permissions.discard(permission)

    def has_permission(self, permission: int) -> bool:
        return permission in self.document_permissions
