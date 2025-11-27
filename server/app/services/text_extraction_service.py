import os

import pdfplumber
import docx

class TextExtractionService:
    """Service to extract text from PDF and DOCX files"""

    async def extract_text(self, filepath: str, filename: str) -> str:
        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            return self._extract_pdf(filepath)
        elif ext == "docx":
            return self._extract_docx(filepath)
        elif ext == "txt":
            return self._extract_txt(filepath)
        else:
            raise ValueError("Unsupported file format")
    
    def _extract_pdf(self, path: str) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def _extract_docx(self, path: str) -> str:
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])

    def _extract_txt(self, path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()
