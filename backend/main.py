from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from pydantic import BaseModel

from backend.rag import answer_question

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

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "pages": pages,
    }

@app.post("/ask")
def ask_question(request: QuestionRequest):
    return answer_question(request.question)