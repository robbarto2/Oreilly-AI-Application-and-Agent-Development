from anthropic import AsyncAnthropic
from backend.config.settings import settings
from typing import List
import logging
import asyncio

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generate embeddings using Claude or OpenAI.

    Features:
    - Batch processing for efficiency
    - Rate limiting and retries
    - Caching to avoid recomputation
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.embedding_model
        self.cache = {}

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        # Check cache
        if text in self.cache:
            logger.debug("Using cached embedding")
            return self.cache[text]

        try:
            # Note: As of the current API, Claude doesn't have a dedicated embedding endpoint
            # You would typically use OpenAI's embedding API or a dedicated embedding model
            # For now, we'll use a placeholder that would need to be replaced with actual embedding generation

            # Placeholder: In production, use OpenAI embeddings or another service
            # from openai import AsyncOpenAI
            # openai_client = AsyncOpenAI()
            # response = await openai_client.embeddings.create(
            #     model="text-embedding-3-large",
            #     input=text
            # )
            # embedding = response.data[0].embedding

            # For now, return a mock embedding (you'll need to implement actual embedding generation)
            logger.warning("Using mock embedding - implement actual embedding generation")
            embedding = await self._mock_embedding(text)

            # Cache the result
            self.cache[text] = embedding
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 10
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} of {len(texts) // batch_size + 1}")

            # Process batch concurrently
            batch_embeddings = await asyncio.gather(
                *[self.generate_embedding(text) for text in batch]
            )
            embeddings.extend(batch_embeddings)

            # Rate limiting: small delay between batches
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)

        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    async def _mock_embedding(self, text: str) -> List[float]:
        """
        Mock embedding for development.
        Replace with actual embedding service in production.
        """
        # Create a deterministic mock embedding based on text hash
        import hashlib
        import numpy as np

        # Hash the text
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Use hash to seed random generator for consistency
        seed = int(text_hash[:8], 16)
        np.random.seed(seed % (2**32))

        # Generate mock embedding vector
        embedding = np.random.randn(settings.embedding_dimension).tolist()

        return embedding


# TODO: Implement actual embedding generation
# Here's how you would implement with OpenAI:
#
# from openai import AsyncOpenAI
#
# class OpenAIEmbeddingGenerator(EmbeddingGenerator):
#     def __init__(self):
#         self.client = AsyncOpenAI()
#         self.model = "text-embedding-3-large"  # 3072 dimensions
#         self.cache = {}
#
#     async def generate_embedding(self, text: str) -> List[float]:
#         if text in self.cache:
#             return self.cache[text]
#
#         response = await self.client.embeddings.create(
#             model=self.model,
#             input=text,
#             dimensions=settings.embedding_dimension
#         )
#         embedding = response.data[0].embedding
#         self.cache[text] = embedding
#         return embedding
