import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class EmbeddingProvider:

    def embed(
        self,
        text,
        task_type="RETRIEVAL_QUERY",
    ):
        raise NotImplementedError


class GeminiEmbeddingProvider(EmbeddingProvider):

    MODEL = "gemini-embedding-001"
    OUTPUT_DIMENSIONALITY = 384

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def embed(
        self,
        text,
        task_type="RETRIEVAL_QUERY",
    ):

        if not text or not text.strip():
            return []

        result = self.client.models.embed_content(
            model=self.MODEL,
            contents=text.strip(),
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=(
                    self.OUTPUT_DIMENSIONALITY
                ),
            ),
        )

        embedding = result.embeddings[0].values

        return embedding