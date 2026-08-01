from dotenv import load_dotenv
from pathlib import Path

from groq import Groq
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

import os
import shutil

# -------------------- Load .env --------------------
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print("Looking for:", env_path)
print("Loaded:", env_path.exists())


# -------------------- Groq Client --------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# -------------------- FastAPI --------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Storage --------------------

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

documents = {}

# -------------------- Home --------------------

@app.get("/")
def home():
    return {
        "message": "Document Understanding Platform is Running"
    }

# -------------------- Upload PDF --------------------

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    print("Uploaded filename:", file.filename)

    documents.clear()

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    documents[file.filename] = text

    return {
        "message": "File uploaded successfully!",
        "filename": file.filename
    }

# -------------------- Read PDF --------------------

@app.get("/read/{filename}")
def read_pdf(filename: str):

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return {
        "filename": filename,
        "content": text
    }

# -------------------- Show Documents --------------------

@app.get("/documents")
def show_documents():
    return documents

# -------------------- Ask Questions --------------------

@app.post("/ask")
def ask_question(question: str = Body(..., embed=True)):

    if len(documents) == 0:
        return {
            "answer": "No documents uploaded.",
            "source": None
        }

    document_text = ""
    sources = []

    for filename, text in documents.items():
        document_text += f"\n\nDocument: {filename}\n{text}"
        sources.append(filename)

    prompt = f"""
You are a document assistant.

Answer ONLY using the uploaded documents.

If the answer is not present in the uploaded documents, reply exactly:

I could not find that information in the uploaded documents.

Documents:

{document_text}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You answer questions only from the uploaded documents."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "source": sources
    }