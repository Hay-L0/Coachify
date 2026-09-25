from .chunker import chunk_text
from .embeddings import GeminiEmbeddingProvider
from .repository import (
    create_knowledge_chunk,
    delete_session_knowledge,
)


class KnowledgeIngestionService:

    def __init__(
        self,
        embedding_provider=None,
    ):
        self.embedding_provider = (
            embedding_provider
            or GeminiEmbeddingProvider()
        )

    def ingest_session_context(
        self,
        session_id,
        user_id,
        resume_content=None,
        job_description=None,
    ):

        delete_session_knowledge(
            session_id
        )

        documents = [
            (
                "resume",
                resume_content,
            ),
            (
                "job_description",
                job_description,
            ),
        ]

        inserted_chunks = []

        for source, content in documents:

            if not content or not content.strip():
                continue

            chunks = chunk_text(
                content.strip()
            )

            for chunk in chunks:

                embedding = (
                    self.embedding_provider.embed(
                        chunk,
                        task_type=(
                            "RETRIEVAL_DOCUMENT"
                        ),
                    )
                )

                knowledge = create_knowledge_chunk(
                    session_id=session_id,
                    user_id=user_id,
                    source=source,
                    content=chunk,
                    embedding=embedding,
                )

                inserted_chunks.append(
                    knowledge
                )

        return inserted_chunks