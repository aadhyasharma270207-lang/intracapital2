import os
import sys
import glob
from app.db.database import SessionLocal, init_db
from app.db import models
from app.utils.taxonomy import AssetType
from app.services.doc_parser import DocumentParser
from app.services.qdrant_service import qdrant_service
from app.services.neo4j_service import neo4j_service
from app.utils.logger import logger

DEMO_DIR = os.path.abspath("./demo_data")

FILE_ASSET_MAP = {
    "warehouse_sensor_report.txt": AssetType.SENSOR_DATA.value,
    "logistics_cold_chain_report.txt": AssetType.HISTORICAL_PROJECT.value,
    "customer_feedback.csv": AssetType.CUSTOMER_FEEDBACK.value,
    "manufacturing_iot_log.json": AssetType.MANUFACTURING_LOG.value,
    "patent_thermal_monitoring.txt": AssetType.PATENT.value,
    "product_specs_hvac.txt": AssetType.PRODUCT.value,
    "market_trends_research.json": AssetType.RESEARCH.value,
}


def seed():
    logger.info("[SEED] Initializing database...")
    init_db()
    db = SessionLocal()

    company_name = "Intracapital Corp"
    company = db.query(models.Company).filter(models.Company.name == company_name).first()
    if not company:
        company = models.Company(name=company_name, industry="Industrial IoT & Thermal Intelligence")
        db.add(company)
        db.commit()
        db.refresh(company)

    logger.info(f"[SEED] Ingesting demo dataset for '{company_name}'...")

    for file_name, asset_type in FILE_ASSET_MAP.items():
        file_path = os.path.join(DEMO_DIR, file_name)
        if not os.path.exists(file_path):
            logger.warning(f"[SEED] Demo file not found: {file_path}")
            continue

        # Create Document record
        doc_id = f"demo-doc-{file_name.split('.')[0]}"
        ext = os.path.splitext(file_name)[1].replace(".", "").upper()

        db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if not db_doc:
            db_doc = models.Document(
                id=doc_id,
                company_id=company.id,
                file_name=file_name,
                file_type=ext,
                file_path=file_path,
                asset_type=asset_type,
                status="processing"
            )
            db.add(db_doc)

        asset_name = file_name.split(".")[0].replace("_", " ").title()
        db_asset = db.query(models.Asset).filter(models.Asset.document_id == doc_id).first()
        if not db_asset:
            db_asset = models.Asset(
                company_id=company.id,
                document_id=doc_id,
                name=asset_name,
                asset_type=asset_type,
                description=f"Synthetic demo asset '{asset_name}'",
                source_file=file_name
            )
            db.add(db_asset)
            db.commit()
            db.refresh(db_asset)

        # Parse & Chunk
        chunks = DocumentParser.parse_file(
            file_path=file_path,
            document_id=doc_id,
            source_file=file_name,
            asset_type=asset_type,
            company=company_name
        )

        chunk_dicts = [c.to_dict() for c in chunks]
        qdrant_service.insert_chunks(chunk_dicts)

        # Graph node & edges
        neo4j_service.create_node("Company", {"id": company.id, "name": company.name})
        neo4j_service.create_node(asset_type.capitalize(), {
            "id": db_asset.id,
            "name": db_asset.name,
            "asset_type": asset_type,
            "source_file": file_name
        })
        neo4j_service.create_relationship("Company", company.id, "OWNS", asset_type.capitalize(), db_asset.id)

        db_doc.chunk_count = len(chunks)
        db_doc.status = "processed"
        db.commit()

        logger.info(f"[SEED] Successfully ingested '{file_name}' ({len(chunks)} chunks).")

    db.close()
    logger.info("[SEED] Demo dataset seeding complete!")


if __name__ == "__main__":
    seed()
