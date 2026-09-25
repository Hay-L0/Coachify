from .embeddings import GeminiEmbeddingProvider
from .repository import search_knowledge


class KnowledgeRetriever:

    def __init__(
        self,
        embedding_provider=None,
    ):
        self.embedding_provider = (
            embedding_provider
            or GeminiEmbeddingProvider()
        )

    def retrieve(
        self,
        session_id,
        query,
        limit=5,
        minimum_similarity=0.35,
    ):

        if not query or not query.strip():
            return []

        embedding = self.embedding_provider.embed(
            query.strip(),
            task_type="RETRIEVAL_QUERY",
        )

        results = search_knowledge(
            session_id=session_id,
            embedding=embedding,
            limit=limit,
        )

        return [
            result
            for result in results
            if result["similarity"]
            >= minimum_similarity
        ]


def format_retrieved_context(results):

    if not results:
        return "No relevant candidate context was found."

    sections = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        sections.append(
            f"""Context {index}
Source: {result["source"]}
Similarity: {result["similarity"]:.3f}
Content:
{result["content"]}"""
        )

    return "\n\n".join(sections)