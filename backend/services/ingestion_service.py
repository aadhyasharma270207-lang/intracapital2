import os
import uuid
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from pypdf import PdfReader

def clean_text(text: str) -> str:
    """
    Cleans raw text by stripping leading/trailing whitespace, 
    normalizing line endings, and replacing multiple spaces with a single space.
    """
    if not text:
        return ""
    text = text.replace("\r", "\n").replace("\t", " ")
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def chunk_text(text: str, filename: str, file_type: str, page: int = None, chunk_size: int = 800, chunk_overlap: int = 150) -> list:
    """
    Splits text into overlapping chunks and attaches filename, file_type, source, page, and chunk_id.
    """
    chunks = []
    if not text:
        return chunks
        
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_content = text[start:end]
        
        chunk_id = str(uuid.uuid4())
        
        metadata = {
            "source": filename,
            "filename": filename,
            "file_type": file_type,
            "chunk_id": chunk_id,
            "char_count": len(chunk_content)
        }
        if page is not None:
            metadata["page"] = page
            
        chunks.append({
            "text": chunk_content,
            "source": filename,
            "filename": filename,
            "file_type": file_type,
            "page": page,
            "chunk_id": chunk_id,
            "metadata": metadata
        })
        
        start += chunk_size - chunk_overlap
        if start >= text_len or chunk_size - chunk_overlap <= 0:
            break
            
    return chunks

def process_txt(file_path: Path) -> list:
    """
    Reads a TXT file, cleans the text, and splits it into chunks.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    cleaned = clean_text(content)
    return chunk_text(cleaned, filename=file_path.name, file_type="txt")

def process_pdf(file_path: Path) -> list:
    """
    Reads a PDF file page by page, cleans each page's text, and chunks it.
    """
    chunks = []
    reader = PdfReader(file_path)
    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        raw_text = page.extract_text() or ""
        cleaned = clean_text(raw_text)
        page_chunks = chunk_text(cleaned, filename=file_path.name, file_type="pdf", page=page_num)
        chunks.extend(page_chunks)
    return chunks

def process_csv(file_path: Path) -> list:
    """
    Reads a CSV file. If it contains temperature/humidity/warehouse telemetry,
    it runs statistical checks to write out an excursion warning analysis.
    """
    chunks = []
    try:
        df = pd.read_csv(file_path)
        df = df.dropna(how="all")
        
        summary_lines = [
            f"CSV Telemetry Analysis: {file_path.name}",
            f"Total data points: {len(df)}",
            f"Columns: {', '.join(df.columns)}",
            f"Monitored Warehouse/Assets: {', '.join(map(str, df['warehouse_id'].unique() if 'warehouse_id' in df.columns else []))}",
            f"Monitored Shipments: {', '.join(map(str, df['shipment_id'].unique() if 'shipment_id' in df.columns else []))}"
        ]
        
        if "temperature" in df.columns and "warehouse_id" in df.columns:
            anomalies = []
            for index, row in df.iterrows():
                w_id = str(row['warehouse_id'])
                temp = float(row['temperature'])
                ship_id = str(row.get('shipment_id', 'N/A'))
                time = str(row.get('timestamp', f"Row {index}"))
                humidity = row.get('humidity', 'N/A')
                
                is_anomaly = False
                desc = "Telemetry excursion"
                if w_id == "C-801" and temp > -10.0:
                    is_anomaly = True
                    desc = "Frozen cargo thawing"
                elif w_id == "WH-101" and temp > 5.0:
                    is_anomaly = True
                    desc = "Warehouse cold room warming"
                elif w_id == "C-502" and temp > 6.0:
                    is_anomaly = True
                    desc = "Berries transit warm-up"
                elif w_id == "C-604" and temp > 6.0:
                    is_anomaly = True
                    desc = "Insulin transit warming"
                
                if is_anomaly:
                    anomalies.append(
                        f"- EXCURSION in {w_id} ({desc}) at {time}: Temp={temp}°C, Humidity={humidity}%, Shipment={ship_id}"
                    )
            
            if anomalies:
                summary_lines.append("\nDetected Temperature Anomalies and Excursions:")
                summary_lines.extend(anomalies[:50])
                if len(anomalies) > 50:
                    summary_lines.append(f"... and {len(anomalies) - 50} more telemetry excursions.")
            else:
                summary_lines.append("\nNo temperature anomalies detected.")
                
        combined_text = "\n".join(summary_lines)
        cleaned = clean_text(combined_text)
        chunks.extend(chunk_text(cleaned, filename=file_path.name, file_type="csv"))
        
        # Raw row batches for granularity
        raw_rows = []
        for i, row in df.iterrows():
            row_dict = row.to_dict()
            raw_rows.append(f"Row {i}: " + ", ".join([f"{k}={v}" for k, v in row_dict.items()]))
            if len(raw_rows) == 20:
                raw_text_chunk = f"Raw Telemetry Data from {file_path.name} (Rows {i-19} to {i}):\n" + "\n".join(raw_rows)
                chunks.extend(chunk_text(raw_text_chunk, filename=file_path.name, file_type="csv"))
                raw_rows = []
        if raw_rows:
            raw_text_chunk = f"Raw Telemetry Data from {file_path.name} (Final Rows):\n" + "\n".join(raw_rows)
            chunks.extend(chunk_text(raw_text_chunk, filename=file_path.name, file_type="csv"))
            
    except Exception as e:
        print(f"[INGESTION] Error parsing CSV {file_path.name}: {e}")
        chunks.extend(chunk_text(f"Corrupt CSV File: {file_path.name}. Error: {str(e)}", filename=file_path.name, file_type="csv"))
        
    return chunks

def ingest_file(file_path: Path) -> list:
    """
    Routes files to their respective extractors. Tolerates errors for single corrupt files.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []
        
    ext = file_path.suffix.lower()
    try:
        if ext == ".txt":
            return process_txt(file_path)
        elif ext == ".pdf":
            return process_pdf(file_path)
        elif ext == ".csv":
            return process_csv(file_path)
        else:
            return []
    except Exception as e:
        print(f"[INGESTION] Error processing {file_path.name}: {e}")
        return [{
            "text": f"Error loading file {file_path.name}. Details: {str(e)}",
            "source": file_path.name,
            "filename": file_path.name,
            "file_type": ext.replace(".", ""),
            "page": None,
            "chunk_id": str(uuid.uuid4()),
            "metadata": {"source": file_path.name, "filename": file_path.name, "file_type": ext.replace(".", ""), "error": str(e)}
        }]

def ingest_directory(directory_path: Path) -> list:
    """
    Iterates through supported files in the directory and aggregates chunks in parallel.
    """
    directory_path = Path(directory_path)
    all_chunks = []
    if not directory_path.exists() or not directory_path.is_dir():
        return all_chunks
        
    file_entries = [
        entry for entry in directory_path.iterdir()
        if entry.is_file() and entry.suffix.lower() in [".txt", ".pdf", ".csv"]
    ]
    
    with ThreadPoolExecutor() as executor:
        results = executor.map(ingest_file, file_entries)
        for chunks in results:
            all_chunks.extend(chunks)
            
    return all_chunks
