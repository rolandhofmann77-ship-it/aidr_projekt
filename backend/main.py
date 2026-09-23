from pathlib import Path
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from docx import Document
import psycopg
from pydantic import BaseModel
from backend.rag import answer_question, embedding_model

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def extract_text_from_pdf(file_path: Path) -> list[dict]:
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "page": page_number,
                "text": text,
            }
        )

    return pages

def extract_text_from_docx(file_path: Path) -> list[dict]:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    full_text = "\n".join(paragraphs)

    return [
        {
            "page": 1,
            "text": full_text,
        }
    ]

def chunk_text(
    text: str,
    target_size: int = 1200,
    max_size: int = 1600,
    overlap: int = 250,
) -> list[str]:
    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    def split_into_sentences(paragraph: str) -> list[str]:
        sentences = []
        current_sentence = ""

        for character in paragraph:
            current_sentence += character

            if character in ".!?":
                sentence = current_sentence.strip()

                if sentence:
                    sentences.append(sentence)

                current_sentence = ""

        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        return sentences

    def create_overlap(sentences: list[str]) -> str:
        overlap_sentences = []
        current_length = 0

        for sentence in reversed(sentences):
            sentence_length = len(sentence)

            if current_length + sentence_length > overlap:
                break

            overlap_sentences.insert(0, sentence)
            current_length += sentence_length

        return " ".join(overlap_sentences)

    for paragraph in paragraphs:
        sentences = split_into_sentences(paragraph)

        for sentence in sentences:
            if not current_chunk:
                current_chunk = sentence
                continue

            candidate = f"{current_chunk} {sentence}"

            if len(candidate) <= target_size:
                current_chunk = candidate
                continue

            chunks.append(current_chunk)

            overlap_text = create_overlap(
                split_into_sentences(current_chunk)
            )

            if overlap_text:
                current_chunk = f"{overlap_text} {sentence}"
            else:
                current_chunk = sentence

            if len(current_chunk) > max_size:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

@app.get("/")
def read_root():
    return {"message": "AIDR Backend läuft!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    pages = []

    if file.content_type == "application/pdf":
        pages = extract_text_from_pdf(file_path)

    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        pages = extract_text_from_docx(file_path)

    else:
        return {
            "message": "Dateiformat wird nicht unterstützt.",
            "filename": file.filename,
        }

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
                INSERT INTO documents (filename, content_type)
                VALUES (%s, %s)
                RETURNING id
                """,
                (file.filename, file.content_type),
            )

            document_id = cursor.fetchone()[0]

            chunk_index = 0

            for page in pages:
                page_text = page["text"]

                chunks = chunk_text(page_text)

                for chunk in chunks:
                    embedding = embedding_model.encode(chunk).tolist()

                    cursor.execute(
                        """
                        INSERT INTO document_chunks (
                            document_id,
                            chunk_index,
                            content,
                            page_number,
                            embedding
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            document_id,
                            chunk_index,
                            chunk,
                            page["page"],
                            embedding,
                        ),
                    )

                    chunk_index += 1

        connection.commit()

    return {
        "document_id": document_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "pages": pages,
        "chunks": chunk_index,
    }

@app.get("/documents")
def list_documents():
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
                    id,
                    filename,
                    content_type,
                    uploaded_at
                FROM documents
                ORDER BY uploaded_at DESC
                """
            )

            documents = cursor.fetchall()

    return [
        {
            "id": document[0],
            "filename": document[1],
            "content_type": document[2],
            "uploaded_at": document[3],
        }
        for document in documents
    ]

@app.delete("/documents/{document_id}")
def delete_document(document_id: int):
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
                DELETE FROM documents
                WHERE id = %s
                RETURNING id, filename
                """,
                (document_id,),
            )

            deleted_document = cursor.fetchone()

        connection.commit()

    if deleted_document is None:
        return {
            "message": "Dokument nicht gefunden",
            "document_id": document_id,
        }

    return {
        "message": "Dokument gelöscht",
        "document_id": deleted_document[0],
        "filename": deleted_document[1],
    }

@app.post("/ask")
def ask_question(request: QuestionRequest):
    return answer_question(request.question)