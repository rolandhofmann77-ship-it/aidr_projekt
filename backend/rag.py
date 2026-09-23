from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer
import psycopg


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
GEMINI_MODEL_NAME = "gemini-3.6-flash"


embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY wurde nicht gefunden.")


gemini_client = genai.Client(api_key=api_key)


def answer_question(question: str) -> dict:
    question_embedding = embedding_model.encode(question).tolist()

    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    document_chunks.id,
                    document_chunks.document_id,
                    documents.filename,
                    document_chunks.page_number,
                    document_chunks.content,
                    document_chunks.embedding <=> %s::vector AS distance
                FROM document_chunks
                JOIN documents
                    ON documents.id = document_chunks.document_id
                WHERE document_chunks.embedding IS NOT NULL
                ORDER BY document_chunks.embedding <=> %s::vector
                LIMIT 3
                """,
                (question_embedding, question_embedding),
            )

            results = cursor.fetchall()

    context_parts = []

    sources = []

    for chunk_id, document_id, filename, page_number, content, distance in results:
        context_parts.append(
            f"[Datei: {filename}, Seite {page_number}]\n{content}"
        )

        sources.append(
            {
                "document_id": document_id,
                "filename": filename,
                "page": page_number,
                "distance": distance,
            }
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
Beantworte die folgende Frage ausschließlich anhand des bereitgestellten
Dokumentkontexts.

Frage:
{question}

Dokumentkontext:
{context}

Wenn der Kontext keine ausreichende Information enthält, sage das offen.

Antworte auf Deutsch.
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
    )

    return {
        "question": question,
        "answer": response.text,
        "sources": sources,
    }