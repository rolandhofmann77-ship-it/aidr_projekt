from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "AIDR Backend läuft!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }