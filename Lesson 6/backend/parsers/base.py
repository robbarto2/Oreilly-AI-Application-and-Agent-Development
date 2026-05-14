from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ParsedContent(BaseModel):
    """Hierarchical content structure preserving document semantics"""

    title: str
    content: str
    item_type: str
    children: List["ParsedContent"] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sequence_order: int = 0

    class Config:
        arbitrary_types_allowed = True


class DocumentParser(ABC):
    """Abstract base class for document parsers"""

    @abstractmethod
    async def parse(self, file_path: str) -> ParsedContent:
        """
        Parse document and return hierarchical structure.

        Args:
            file_path: Path to the document file

        Returns:
            ParsedContent: Root node of hierarchical content tree
        """
        pass

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """
        Check if this parser supports the given file type.

        Args:
            file_path: Path to check

        Returns:
            bool: True if this parser can handle the file
        """
        pass
