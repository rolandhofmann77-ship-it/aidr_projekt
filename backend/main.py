from pathlib import Path
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
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

            for page in pages:
                page_text = page["text"]

                embedding = embedding_model.encode(page_text).tolist()

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
                        page["page"] - 1,
                        page_text,
                        page["page"],
                        embedding,
                    ),
                )

        connection.commit()

    return {
        "document_id": document_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "pages": pages,
    }

@app.post("/ask")
def ask_question(request: QuestionRequest):
    return answer_question(request.question)