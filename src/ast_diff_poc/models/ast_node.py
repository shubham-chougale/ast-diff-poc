"""AST node structures for property files."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PropertyNode:
    """Represents a single property key-value pair in a property file."""

    line_number: int  # 1-indexed line number
    key: str
    value: str
    raw_line: str  # Original line content for whitespace preservation
    leading_whitespace: str = ""  # Whitespace before key
    separator: str = "="  # Separator used (= or :)
    trailing_whitespace_before_value: str = ""  # Whitespace after separator
    trailing_whitespace_after_value: str = ""  # Whitespace after value

    def __hash__(self) -> int:
        """Make PropertyNode hashable for use in sets/dicts."""
        return hash((self.line_number, self.key, self.value))

    def __eq__(self, other: object) -> bool:
        """Equality comparison based on key and value."""
        if not isinstance(other, PropertyNode):
            return False
        return self.key == other.key and self.value == other.value

    def is_semantically_equivalent(self, other: "PropertyNode") -> bool:
        """Check if two nodes are semantically equivalent (same key/value, ignoring whitespace)."""
        return self.key == other.key and self.value == other.value


@dataclass
class EmptyLineNode:
    """Represents an empty line in a property file."""

    line_number: int


@dataclass
class CommentNode:
    """Represents a comment line in a property file."""

    line_number: int
    content: str  # Comment content without the # prefix


@dataclass
class PropertyFileAST:
    """Container for all nodes in a property file."""

    nodes: List[PropertyNode]
    empty_lines: List[EmptyLineNode]
    comments: List[CommentNode]
    file_path: Optional[str] = None

    def get_node_by_key(self, key: str) -> Optional[PropertyNode]:
        """Get the first node with the given key."""
        for node in self.nodes:
            if node.key == key:
                return node
        return None

    def get_nodes_by_key(self, key: str) -> List[PropertyNode]:
        """Get all nodes with the given key (for duplicate keys)."""
        return [node for node in self.nodes if node.key == key]

    def get_node_at_line(self, line_number: int) -> Optional[PropertyNode]:
        """Get the node at a specific line number."""
        for node in self.nodes:
            if node.line_number == line_number:
                return node
        return None

    def __len__(self) -> int:
        """Return the number of property nodes."""
        return len(self.nodes)
