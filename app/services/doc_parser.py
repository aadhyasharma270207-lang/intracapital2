import os
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None


class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        source_file: str,
        content: str,
        asset_type: str,
        company: str,
        page_number: Optional[int] = None,
        section_title: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.source_file = source_file
        self.content = content
        self.asset_type = asset_type
        self.company = company
        self.page_number = page_number
        self.section_title = section_title
        self.timestamp = timestamp or datetime.datetime.utcnow().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "source_file": self.source_file,
            "content": self.content,
            "asset_type": self.asset_type,
            "company": self.company,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class DocumentParser:
    @staticmethod
    def parse_file(
        file_path: str,
        document_id: str,
        source_file: str,
        asset_type: str,
        company: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[DocumentChunk]:
        ext = os.path.splitext(source_file)[1].lower()

        if ext == ".txt":
            return DocumentParser._parse_txt(file_path, document_id, source_file, asset_type, company, chunk_size, overlap)
        elif ext == ".pdf":
            return DocumentParser._parse_pdf(file_path, document_id, source_file, asset_type, company, chunk_size, overlap)
        elif ext == ".docx":
            return DocumentParser._parse_docx(file_path, document_id, source_file, asset_type, company, chunk_size, overlap)
        elif ext in [".csv", ".tsv"]:
            return DocumentParser._parse_csv(file_path, document_id, source_file, asset_type, company)
        elif ext in [".xlsx", ".xls"]:
            return DocumentParser._parse_excel(file_path, document_id, source_file, asset_type, company)
        elif ext == ".json":
            return DocumentParser._parse_json(file_path, document_id, source_file, asset_type, company)
        else:
            return DocumentParser._parse_txt(file_path, document_id, source_file, asset_type, company, chunk_size, overlap)

    @staticmethod
    def _create_chunks_from_text(
        text: str,
        document_id: str,
        source_file: str,
        asset_type: str,
        company: str,
        page_number: Optional[int] = None,
        section_title: Optional[str] = None,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[DocumentChunk]:
        text = text.strip()
        if not text:
            return []

        chunks = []
        words = text.split()
        if len(words) <= chunk_size:
            chunk_text = " ".join(words)
            chunks.append(DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                source_file=source_file,
                content=chunk_text,
                asset_type=asset_type,
                company=company,
                page_number=page_number,
                section_title=section_title
            ))
            return chunks

        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append(DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                source_file=source_file,
                content=chunk_text,
                asset_type=asset_type,
                company=company,
                page_number=page_number,
                section_title=section_title
            ))
            i += (chunk_size - overlap)

        return chunks

    @staticmethod
    def _parse_txt(file_path, document_id, source_file, asset_type, company, chunk_size, overlap) -> List[DocumentChunk]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return DocumentParser._create_chunks_from_text(
            text, document_id, source_file, asset_type, company, chunk_size=chunk_size, overlap=overlap
        )

    @staticmethod
    def _parse_pdf(file_path, document_id, source_file, asset_type, company, chunk_size, overlap) -> List[DocumentChunk]:
        chunks = []
        if PdfReader is not None:
            try:
                reader = PdfReader(file_path)
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    page_chunks = DocumentParser._create_chunks_from_text(
                        page_text, document_id, source_file, asset_type, company,
                        page_number=page_idx + 1, chunk_size=chunk_size, overlap=overlap
                    )
                    chunks.extend(page_chunks)
                if chunks:
                    return chunks
            except Exception:
                pass

        # Fallback text reading if pdf parsing failed or empty
        return DocumentParser._parse_txt(file_path, document_id, source_file, asset_type, company, chunk_size, overlap)

    @staticmethod
    def _parse_docx(file_path, document_id, source_file, asset_type, company, chunk_size, overlap) -> List[DocumentChunk]:
        chunks = []
        if docx is not None:
            try:
                doc = docx.Document(file_path)
                current_section = "General"
                section_text = []

                for para in doc.paragraphs:
                    if para.style.name.startswith("Heading"):
                        if section_text:
                            full_text = "\n".join(section_text)
                            chunks.extend(DocumentParser._create_chunks_from_text(
                                full_text, document_id, source_file, asset_type, company,
                                section_title=current_section, chunk_size=chunk_size, overlap=overlap
                            ))
                            section_text = []
                        current_section = para.text.strip()
                    else:
                        if para.text.strip():
                            section_text.append(para.text.strip())

                if section_text:
                    full_text = "\n".join(section_text)
                    chunks.extend(DocumentParser._create_chunks_from_text(
                        full_text, document_id, source_file, asset_type, company,
                        section_title=current_section, chunk_size=chunk_size, overlap=overlap
                    ))

                if chunks:
                    return chunks
            except Exception:
                pass

        return DocumentParser._parse_txt(file_path, document_id, source_file, asset_type, company, chunk_size, overlap)

    @staticmethod
    def _parse_csv(file_path, document_id, source_file, asset_type, company) -> List[DocumentChunk]:
        try:
            df = pd.read_csv(file_path)
            records = df.to_dict(orient="records")
            chunks = []
            # Group records into chunks of 10 rows
            for idx in range(0, len(records), 10):
                batch = records[idx:idx + 10]
                text_lines = [f"Record {idx + i + 1}: " + ", ".join([f"{k}={v}" for k, v in row.items()]) for i, row in enumerate(batch)]
                content = "\n".join(text_lines)
                chunks.append(DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    source_file=source_file,
                    content=content,
                    asset_type=asset_type,
                    company=company,
                    section_title=f"Rows {idx+1} to {idx+len(batch)}"
                ))
            return chunks
        except Exception:
            return DocumentParser._parse_txt(file_path, document_id, source_file, asset_type, company, 500, 50)

    @staticmethod
    def _parse_excel(file_path, document_id, source_file, asset_type, company) -> List[DocumentChunk]:
        try:
            xls = pd.ExcelFile(file_path)
            chunks = []
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                records = df.to_dict(orient="records")
                for idx in range(0, len(records), 10):
                    batch = records[idx:idx + 10]
                    text_lines = [f"Sheet [{sheet_name}] Row {idx + i + 1}: " + ", ".join([f"{k}={v}" for k, v in row.items()]) for i, row in enumerate(batch)]
                    content = "\n".join(text_lines)
                    chunks.append(DocumentChunk(
                        chunk_id=str(uuid.uuid4()),
                        document_id=document_id,
                        source_file=source_file,
                        content=content,
                        asset_type=asset_type,
                        company=company,
                        section_title=sheet_name
                    ))
            return chunks
        except Exception:
            return DocumentParser._parse_txt(file_path, document_id, source_file, asset_type, company, 500, 50)

    @staticmethod
    def _parse_json(file_path, document_id, source_file, asset_type, company) -> List[DocumentChunk]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            chunks = []
            if isinstance(data, list):
                for idx in range(0, len(data), 5):
                    batch = data[idx:idx + 5]
                    content = json.dumps(batch, indent=2)
                    chunks.append(DocumentChunk(
                        chunk_id=str(uuid.uuid4()),
                        document_id=document_id,
                        source_file=source_file,
                        content=content,
                        asset_type=asset_type,
                        company=company,
                        section_title=f"JSON Array Items {idx} to {idx+len(batch)-1}"
                    ))
            elif isinstance(data, dict):
                for key, val in data.items():
                    content = f"Key: {key}\n" + json.dumps(val, indent=2)
                    chunks.append(DocumentChunk(
                        chunk_id=str(uuid.uuid4()),
                        document_id=document_id,
                        source_file=source_file,
                        content=content,
                        asset_type=asset_type,
                        company=company,
                        section_title=f"Field: {key}"
                    ))
            else:
                chunks.append(DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    source_file=source_file,
                    content=str(data),
                    asset_type=asset_type,
                    company=company
                ))
            return chunks
        except Exception:
            return DocumentParser._parse_txt(file_path, document_id, source_file, asset_type, company, 500, 50)
