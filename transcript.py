import PyPDF2
import os
from io import BytesIO

class DocumentLoader():
    """Load text from uploaded documents (PDF, TXT, etc.)"""
    
    def extract_text_from_pdf(self, file_bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def extract_text_from_txt(self, file_bytes) -> str:
        """Extract text from TXT file."""
        try:
            return file_bytes.decode('utf-8')
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return ""
    
    def extract_text_from_docx(self, file_bytes) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            doc = Document(BytesIO(file_bytes))
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
    
    def extract_text(self, file_bytes, file_name: str) -> str:
        """Extract text from uploaded file based on extension."""
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_bytes)
        elif file_ext == '.txt':
            return self.extract_text_from_txt(file_bytes)
        elif file_ext == '.docx':
            return self.extract_text_from_docx(file_bytes)
        else:
            print(f"Unsupported file type: {file_ext}")
            return ""

