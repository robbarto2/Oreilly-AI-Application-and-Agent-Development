from backend.parsers.base import ParsedContent
from backend.config.settings import settings
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class SemanticChunker:
    """
    Semantic chunker that respects content hierarchy.

    Key principle: Don't split mid-section or mid-concept.
    Preserve parent-child relationships and maintain context windows.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    async def chunk_content(
        self, parsed_content: ParsedContent, parent_context: str = ""
    ) -> List[Tuple[str, ParsedContent, str]]:
        """
        Chunk content hierarchically, preserving structure.

        Args:
            parsed_content: Root of parsed content tree
            parent_context: Context from parent nodes

        Returns:
            List of tuples: (chunk_text, original_node, parent_context)
        """
        chunks = []

        # Build context from parent
        current_context = parent_context
        if parsed_content.title:
            current_context = f"{parent_context}\n{parsed_content.title}".strip()

        # Check if this node's content should be chunked
        if parsed_content.content:
            node_chunks = self._chunk_text(
                parsed_content.content,
                current_context,
            )

            for chunk_text in node_chunks:
                chunks.append((chunk_text, parsed_content, current_context))

        # Recursively process children
        for child in parsed_content.children:
            child_chunks = await self.chunk_content(child, current_context)
            chunks.extend(child_chunks)

        return chunks

    def _chunk_text(self, text: str, context: str) -> List[str]:
        """
        Split text into chunks respecting sentence boundaries.

        Args:
            text: Text to chunk
            context: Context to prepend (e.g., section titles)

        Returns:
            List of text chunks with context
        """
        if not text:
            return []

        # If text is short enough, return as single chunk
        if len(text) <= self.chunk_size:
            return [f"{context}\n\n{text}".strip() if context else text]

        # Split by sentences (simple heuristic)
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = []
        current_length = len(context) + 2  # +2 for "\n\n"

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds chunk size, start new chunk
            if current_chunk and (current_length + sentence_length > self.chunk_size):
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                if context:
                    chunk_text = f"{context}\n\n{chunk_text}"
                chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk, self.chunk_overlap
                )
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk) + len(context) + 2

            else:
                current_chunk.append(sentence)
                current_length += sentence_length + 1  # +1 for space

        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if context:
                chunk_text = f"{context}\n\n{chunk_text}"
            chunks.append(chunk_text)

        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences (simple heuristic).

        For production, consider using nltk.sent_tokenize or spacy.
        """
        import re

        # Simple sentence splitting on period, exclamation, question mark
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_sentences(self, sentences: List[str], overlap_size: int) -> List[str]:
        """Get last N characters worth of sentences for overlap"""
        if not sentences:
            return []

        overlap_sentences = []
        overlap_length = 0

        for sentence in reversed(sentences):
            if overlap_length + len(sentence) > overlap_size:
                break
            overlap_sentences.insert(0, sentence)
            overlap_length += len(sentence)

        return overlap_sentences
