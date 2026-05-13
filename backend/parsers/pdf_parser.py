import fitz  # PyMuPDF
from backend.parsers.base import DocumentParser, ParsedContent
from typing import List
import logging
import re

logger = logging.getLogger(__name__)


class PDFParser(DocumentParser):
    """Parser for PDF files with layout preservation"""

    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith('.pdf')

    async def parse(self, file_path: str) -> ParsedContent:
        """
        Parse PDF file attempting to preserve structure.

        Extracts:
        - Text with layout preservation
        - Page boundaries
        - Attempts to detect sections (heuristic-based)
        """
        try:
            doc = fitz.open(file_path)
            pages = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_content = self._extract_page_content(page, page_num + 1)
                if page_content:
                    pages.append(page_content)

            doc.close()

            root = ParsedContent(
                title=f"PDF Document from {file_path}",
                content=f"PDF document with {len(pages)} pages",
                item_type="document",
                children=pages,
                metadata={"total_pages": len(pages)},
                sequence_order=0,
            )

            logger.info(f"Parsed PDF: {len(pages)} pages from {file_path}")
            return root

        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {e}")
            raise

    def _extract_page_content(self, page, page_num: int) -> ParsedContent:
        """Extract content from a single PDF page"""
        # Extract text with layout preservation
        text = page.get_text("text")

        # Try to extract blocks for better structure
        blocks = page.get_text("blocks")

        # Filter out empty text
        text = text.strip()
        if not text:
            return None

        # Attempt to detect if this is a title page or content page
        is_title_page = page_num == 1 and len(text.split('\n')) < 10

        metadata = {
            "page_number": page_num,
            "is_title_page": is_title_page,
            "block_count": len(blocks),
        }

        return ParsedContent(
            title=f"Page {page_num}",
            content=text,
            item_type="section",
            metadata=metadata,
            sequence_order=page_num,
        )

    def _detect_sections(self, text: str) -> List[str]:
        """
        Heuristic-based section detection.
        Look for common heading patterns.
        """
        # Common heading patterns
        patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS headings
            r'^\d+\.\s+[A-Z]',   # Numbered headings
            r'^Chapter \d+',     # Chapter headings
            r'^Section \d+',     # Section headings
        ]

        sections = []
        for line in text.split('\n'):
            line = line.strip()
            for pattern in patterns:
                if re.match(pattern, line):
                    sections.append(line)
                    break

        return sections
