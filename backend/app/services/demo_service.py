import os
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.repositories.repos import CompanyRepository, AssetRepository, OpportunityRepository, ProcessingJobRepository
from app.services.ingestion_service import IngestionService
from app.services.embeddings_service import EmbeddingsService
from app.services.qdrant_service import QdrantService
from app.services.graph_service import GraphService
from app.models.models import Company, Asset

logger = logging.getLogger(__name__)

# Define file contents directly to write to disk dynamically
FLEET_REPORT_CONTENT = """
FrostLink Logistics: Fleet Operational Performance Audit
Date: 2026-06-15
Author: Director of Operations, Logistics Division

EXECUTIVE SUMMARY
This internal operational audit evaluates refrigerated logistics across our primary trucking fleet (75 heavy trucks). Over the last 12 months, we have observed a 15% increase in cargo spoilage write-offs, costing the firm approximately $420,000 in customer refunds and insurance deductibles. 

DELIVERY DELAYS & TEMPERATURE DEVIATIONS
Our GPS telemetry shows Route 101 (Los Angeles - Phoenix) and Route 5 (Seattle - Portland) suffer from heavy traffic delays. On Route 101, transit times have increased by an average of 45 minutes. More importantly, older ThermoKing cargo chilling compressors fail to maintain the target temperature of 2.0°C during extended gridlocks when the vehicle engine is idling. 

We lack real-time temperature telemetry inside the truck cabs. Drivers are only aware of cooling failures when they arrive at customer distribution centers and run a manual temperature probe, by which time the cargo (fresh produce, vaccines) is already ruined.

RECOMMENDATIONS
1. We must install real-time IoT temperature sensor beacons inside all active refrigerated trailer containers.
2. Link GPS routing systems with active container ambient trackers to alert dispatchers when a temperature drift exceeds 4.0°C.
"""

REFRIGERATION_AUDIT_CONTENT = """
FrostLink Logistics: Infrastructure & Equipment Health Assessment
Department: Facilities Maintenance & Engineering
Facility: LA Cold Storage Warehouse Complex

COMPRESSOR AUDIT
A diagnostic review was conducted on the 12 industrial compressors powering Cold Storage Room 3.
Compressor C-9 and C-12 have exceeded 25,000 hours of continuous operations without rebuild.
Maintenance records indicate Compressor C-9 has shown signs of electrical amperage fluctuations and abnormal vibration. In July, Room 3 experienced a 4-hour temperature spike from 1.5°C to 7.8°C due to unexpected cooling compressor downtime.

SENSOR SYSTEM LIMITATIONS
While temperature sensors are installed inside the rooms, they are wired to a local SCADA panel in the warehouse control center. The system does not dispatch external SMS or pager notifications. A temperature fluctuation over the weekend is not visible until the Monday morning shift.

SYSTEM DEPENDENCIES
- Refrigeration compressors are critical for fresh seafood storage.
- Anomaly drift: When compressor C-9 struggles, temperature climbs at 1.2°C per hour.
"""

COMPLAINTS_CSV_CONTENT = [
    ["ComplaintID", "Customer", "Date", "AssetCategory", "ComplaintText", "RefundRequested"],
    ["C-401", "MediSave Pharma", "2026-07-02", "Logistics Fleet", "Vaccine batch delivered at 7.5 degrees. Required standard is 2.0 to 4.0. Total batch rejected.", "Yes"],
    ["C-402", "FreshFoods Market", "2026-07-10", "Warehouse Room 3", "Fresh salmon pallet had ammonia odor upon delivery, indicating refrigeration drift. Temperature logged 6.8 C.", "Yes"],
    ["C-403", "QuickStop Grocers", "2026-07-14", "Logistics Fleet", "Frozen dairy products partially deflated. Fleet trailer #24 cooling unit appears weak during transit.", "Yes"],
    ["C-404", "MediSave Pharma", "2026-07-28", "Logistics Fleet", "Second cargo temperature issue on LA-Phoenix route. Requesting audit of transport conditions.", "Yes"]
]

TEMP_SAMPLES_CSV_CONTENT = [
    ["SensorID", "Timestamp", "Location", "Temperature_C", "Status"],
    ["SEN-ROOM3-1", "2026-07-20T00:00:00", "Cold Storage Room 3", "2.1", "Normal"],
    ["SEN-ROOM3-1", "2026-07-20T04:00:00", "Cold Storage Room 3", "2.3", "Normal"],
    ["SEN-ROOM3-1", "2026-07-20T08:00:00", "Cold Storage Room 3", "4.8", "Anomaly - Anomaly Drift Detected"],
    ["SEN-ROOM3-1", "2026-07-20T12:00:00", "Cold Storage Room 3", "6.9", "Critical - Temperature Spike"],
    ["SEN-ROOM3-1", "2026-07-20T16:00:00", "Cold Storage Room 3", "7.8", "Critical - Temperature Spike"],
    ["SEN-ROOM3-1", "2026-07-20T20:00:00", "Cold Storage Room 3", "3.2", "Recovery - Unit Reset"]
]

class DemoService:
    @classmethod
    def load_demo_data(cls, db: Session, job_id: str) -> Company:
        """
        Creates FrostLink Logistics company, writes files, triggers full processing pipeline,
        generates 3 predefined business opportunities, and maps them.
        """
        # Step 1: Initialize Job Status
        ProcessingJobRepository.update(db, job_id, current_step="01 Understanding Assets", progress=15.0)
        
        # Check if FrostLink Logistics already exists, clean up if so
        existing_company = db.query(Company).filter(Company.name == "FrostLink Logistics").first()
        if existing_company:
            # Delete old company assets & opportunities
            OpportunityRepository.delete_by_company(db, existing_company.id)
            db.delete(existing_company)
            db.commit()
            
        # Create FrostLink Company
        company = CompanyRepository.create(
            db, 
            name="FrostLink Logistics", 
            description="Refrigerated shipping, supply chain management, and cold storage warehousing operations provider."
        )

        # Create demo uploads folder
        demo_dir = settings.UPLOAD_DIR / "demo"
        demo_dir.mkdir(parents=True, exist_ok=True)

        files_to_create = [
            ("logistics_operations_report.txt", FLEET_REPORT_CONTENT),
            ("refrigeration_equipment_audit.txt", REFRIGERATION_AUDIT_CONTENT),
            ("customer_complaints.csv", COMPLAINTS_CSV_CONTENT),
            ("warehouse_temp_anomalies.csv", TEMP_SAMPLES_CSV_CONTENT)
        ]

        uploaded_assets: List[Asset] = []
        
        # Step 2: Write Files and Ingest
        ProcessingJobRepository.update(db, job_id, current_step="02 Extracting Evidence", progress=30.0)
        for filename, content in files_to_create:
            file_path = demo_dir / filename
            
            # Write physical files to simulate actual ingestion
            if isinstance(content, list):
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(content)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # Ingest through IngestionService
            parsed_data = IngestionService.parse_file(str(file_path), filename)
            
            asset = AssetRepository.create(
                db=db,
                company_id=company.id,
                file_name=filename,
                asset_type="CSV" if filename.endswith(".csv") else "Document",
                department="Operations" if "fleet" in filename or "logistics" in filename else "Maintenance",
                source="Internal Operations Data",
                metadata_json=parsed_data["metadata"],
                content=parsed_data["content"]
            )
            uploaded_assets.append(asset)
            
            # Chunk and Embed
            chunks = IngestionService.chunk_text(parsed_data["content"])
            chunk_records = []
            
            for idx, text_val in enumerate(chunks):
                db_chunk = AssetRepository.create_chunk(
                    db=db,
                    asset_id=asset.id,
                    text=text_val,
                    chunk_index=idx,
                    metadata_json={"file_name": filename}
                )
                
                # Embedding Vector
                vector = EmbeddingsService.get_embedding(text_val)
                chunk_records.append({
                    "id": db_chunk.id,
                    "vector": vector,
                    "payload": {
                        "asset_id": asset.id,
                        "chunk_id": db_chunk.id,
                        "file_name": filename,
                        "text": text_val
                    }
                })
                
            # Store in Qdrant
            QdrantService.index_chunks(collection_name=f"company_{company.id}", chunks=chunk_records)
            AssetRepository.update_status(db, asset.id, "processed")

        # Step 3: Connect Signals in Knowledge Graph
        ProcessingJobRepository.update(db, job_id, current_step="03 Connecting Signals", progress=45.0)
        GraphService.clear_graph()
        
        # Add basic Company Node
        GraphService.add_node(company.id, "Company", {"name": company.name, "description": company.description})
        
        # Add Asset Nodes & Connect them
        for asset in uploaded_assets:
            GraphService.add_node(asset.id, "Asset", {"name": asset.file_name, "type": asset.asset_type})
            GraphService.add_relationship(company.id, asset.id, "OWNS")
            
        # Add specific knowledge nodes representing connected signals
        GraphService.add_node("room_3", "Warehouse", {"name": "Cold Storage Room 3", "location": "LA Facility"})
        GraphService.add_node("c9_compressor", "Technology", {"name": "Compressor C-9", "type": "Cooling Compressor"})
        GraphService.add_node("temp_anomaly", "OperationalProblem", {"name": "Temperature Fluctuations", "severity": "High"})
        GraphService.add_node("spoilage_risk", "OperationalProblem", {"name": "Cargo Food Spoilage", "loss_value": "$420,000"})
        GraphService.add_node("realtime_iot", "Capability", {"name": "Real-time Cold Chain Monitoring", "type": "IoT / SaaS"})
        GraphService.add_node("fleet_routes", "Asset", {"name": "Logistics Routes", "type": "Transit"})

        # Connections
        GraphService.add_relationship("room_3", "c9_compressor", "OPERATED_BY")
        GraphService.add_relationship("c9_compressor", "temp_anomaly", "CAUSES")
        GraphService.add_relationship("temp_anomaly", "spoilage_risk", "INCREASES")
        GraphService.add_relationship("realtime_iot", "temp_anomaly", "MITIGATES")
        GraphService.add_relationship(company.id, "realtime_iot", "POTENTIAL_CAPABILITY")

        # Step 4: AI Analysis
        ProcessingJobRepository.update(db, job_id, current_step="04 Granite Analysis", progress=60.0)
        # In a real environment, we'd query Ollama / Granite here.
        # For the demo company, we load the three designated Opportunities.
        
        # Step 5: Evaluating Opportunities
        ProcessingJobRepository.update(db, job_id, current_step="05 Evaluating Opportunities", progress=75.0)
        
        # Opportunity 1: Cold Chain Intelligence
        opp1 = OpportunityRepository.create(
            db=db,
            company_id=company.id,
            title="Cold Chain Intelligence",
            short_description="AI-powered real-time cold-chain visibility and predictive spoilage monitoring platform utilizing existing warehouse and container temperature sensors.",
            problem="Temperature deviations in warehouse Room 3 and transport vehicles lead to seafood and vaccine spoilage. Manual probing at delivery spots occurs too late.",
            solution="Unify wireless Bluetooth Low Energy (BLE) temperature beacons, vehicle GPS telemetry and historical logs into a real-time tracking interface powered by anomaly detection models.",
            target_customers="Pharmaceutical distributors, specialized food and beverage shippers, third-party logistics (3PL) carriers.",
            industry="Cold Chain Supply Chain Logistics",
            business_model="B2B SaaS subscription per trailer / room monitored.",
            revenue_model="Monthly subscription tier + compliance reporting premium + automated emergency SMS alerts packages.",
            market_potential=94.0,
            feasibility=88.0,
            strategic_fit=91.0,
            asset_reusability=90.0,
            confidence=92.0,
            overall_score=91.4,
            required_resources="Temperature beacon hardware, cellular GPS gateways, backend monitoring service API, dashboard notifications system.",
            existing_assets_used="warehouse_temp_anomalies.csv, customer_complaints.csv, logistics_operations_report.txt",
            key_activities="Hardware sensor staging, predictive thermal anomaly algorithm calibration, enterprise dashboard deployment.",
            key_resources="Existing software systems team, warehouse refrigeration equipment logs, SQLite database records.",
            cost_drivers="AWS IoT Core/messaging streaming costs, sales acquisitions, initial sensor procurement.",
            go_to_market="Deploy internally to prove zero-spoilage rate, then market as a core value proposition to existing shippers.",
            risks="Driver compliance with sensor recharging; cellular coverage deadzones in transit corridors.",
            assumptions="Shippers will pay a premium for certified temperature logs for pharmaceutical compliance.",
            reasoning="We possess high-frequency historical data on temperature drifts and direct customer complaints logs detailing salmon and vaccine write-offs. This forms a clear evidence trace justifying ROI."
        )
        
        # Add BMC Canvas for Opp 1
        OpportunityRepository.create_business_model(
            db=db,
            opportunity_id=opp1.id,
            customer_segments="Food & beverage shipping lines, pharma distributors, grocery networks, 3PL transport companies.",
            value_propositions="Real-time temperature transparency, 90% reduction in cargo spoilage, automated FDA/regulatory temperature compliance logging.",
            channels="Direct enterprise sales, cold storage industry trade shows, supply chain platform plugins.",
            customer_relationships="SLA guarantees, co-development pilots, automated mobile/email notifications.",
            revenue_streams="Subscription ($49/vehicle/month), Setup and integration fee ($1,500/facility), Custom compliance audits ($99/report).",
            key_resources="Predictive thermal drift algorithms, telemetry databases, software engineers, IoT network gateways.",
            key_activities="Sensor data streaming, predictive model calibration, automated work-order alerts routing.",
            key_partners="Cargo insurers (for lower premiums), Bluetooth beacon manufacturers, compliance auditors.",
            cost_structure="Cloud server messaging ingestion, R&D staff, customer success teams, sales campaigns.",
            first_validation="Run a 30-day proof-of-concept pilot on 5 active shipping trucks to confirm beacon telemetry stability."
        )

        # Opportunity 2: Predictive Maintenance Platform
        opp2 = OpportunityRepository.create(
            db=db,
            company_id=company.id,
            title="Predictive Maintenance Platform",
            short_description="Machine learning powered diagnostic scheduler for facilities HVAC systems and truck chilling units.",
            problem="Unscheduled cooling compressor failures (C-9 and C-12 in Room 3) cause emergency maintenance costs and facility-wide temperature warnings.",
            solution="Connect vibration and current telemetry inputs from facility audits to an anomaly classifier. Flag equipment degradation 2-3 weeks before failure.",
            target_customers="Cold storage facilities, commercial food distribution centers, industrial warehouse operations.",
            industry="Industrial IoT (IIoT) & Facilities Tech",
            business_model="SaaS per compressor monitored.",
            revenue_model="Monthly active machine subscription + automated technician dispatch integrations.",
            market_potential=86.0,
            feasibility=84.0,
            strategic_fit=88.0,
            asset_reusability=90.0,
            confidence=88.0,
            overall_score=87.2,
            required_resources="Amperage/vibration clamps, edge gateway software, API linking tool for work-order schedules.",
            existing_assets_used="refrigeration_equipment_audit.txt, customer_complaints.csv",
            key_activities="Acoustic/electrical anomaly threshold training, scheduling automation setup.",
            key_resources="Equipment maintenance history logs, refrigeration audit records.",
            cost_drivers="Telemetry storage capacity, field sales representatives.",
            go_to_market="Leverage internal facilities data to validate savings metrics, then market to partner warehouse chains.",
            risks="Technicians ignoring automated warning cycles; hardware variation between refrigeration compressor brands.",
            assumptions="Amperage spikes correlate directly with bearing friction and compressor thermal load.",
            reasoning="Audit reports show that compressor C-9 and C-12 are running continuously past their service life. Room 3 spikes are trace evidence of unpredicted failure costs."
        )
        
        OpportunityRepository.create_business_model(
            db=db,
            opportunity_id=opp2.id,
            customer_segments="Commercial warehouse operators, pharmaceutical logistics hubs, industrial refrigeration facility managers.",
            value_propositions="Zero unscheduled compressor failures, 30% savings on emergency technician rates, extended equipment service life.",
            channels="Facility management consultants, industrial equipment distributors.",
            customer_relationships="Annual maintenance audits, technical co-engineering support.",
            revenue_streams="Monitoring fee ($89/month/unit), API ERP connection fee ($199/month).",
            key_resources="Failure prediction classifiers, database endpoints, support technicians.",
            key_activities="Equipment diagnostics, alert notifications routing, hardware installation support.",
            key_partners="Refrigeration OEM brands, certified repair networks, insurance companies.",
            cost_structure="Staff engineers, hardware diagnostic toolsets, trade promotions.",
            first_validation="Instrument Compressor C-9 for 60 days to evaluate electric/vibration load anomalies."
        )

        # Opportunity 3: Logistics Optimization AI
        opp3 = OpportunityRepository.create(
            db=db,
            company_id=company.id,
            title="Logistics Optimization AI",
            short_description="Smart dispatching and delivery routing platform balancing refrigeration unit temperature loads and transit congestion.",
            problem="Static routing leads to trucks idling in traffic hot-spots like Route 101, causing increased temperature load and seafood cargo write-offs.",
            solution="Dynamic rerouting algorithm that tracks container heat-loading rates and modifies routes to avoid heavy traffic zones when cargo temperatures begin to rise.",
            target_customers="Perishable goods distribution services, last-mile fresh grocery delivery fleets.",
            industry="Routing & Logistics Optimization SaaS",
            business_model="Usage-based subscription per optimized route.",
            revenue_model="Per-route billing rate + central operator dispatch dashboard license fee.",
            market_potential=85.0,
            feasibility=80.0,
            strategic_fit=84.0,
            asset_reusability=85.0,
            confidence=84.0,
            overall_score=83.6,
            required_resources="Routing database access, GPS API access, dispatcher dashboard portal.",
            existing_assets_used="logistics_operations_report.txt, customer_complaints.csv",
            key_activities="Rerouting engine logic optimization, map API hooks integration.",
            key_resources="Fleet travel history datasets, logistics operations report records.",
            cost_drivers="Map provider search fees, sales acquisition budgets.",
            go_to_market="Partner with mid-size retail grocers to improve scheduling performance metrics.",
            risks="Driver resistance to following dynamic GPS shifts; map query charge costs.",
            assumptions="Live transit times can be accessed via OpenStreetMap or similar traffic layers.",
            reasoning="Operations report lists Route 101 delays as key triggers for cooling unit failures, illustrating the cost impact of traffic delays on thermal load."
        )
        
        OpportunityRepository.create_business_model(
            db=db,
            opportunity_id=opp3.id,
            customer_segments="Local grocers, pharmaceutical transport distributors, last-mile logistics fleets.",
            value_propositions="12% reduction in route times, lower fuel usage by 8%, eliminated late arrival claims.",
            channels="TMS API plugins, direct logistics platform sales, online search campaigns.",
            customer_relationships="Developer community portals, customer service team.",
            revenue_streams="Usage fee ($0.15/route calculated), Dispatcher monitoring platform ($150/month).",
            key_resources="Routing algorithms, traffic maps, telemetry APIs.",
            key_activities="Algorithm training, real-time map styling, driver feedback loops.",
            key_partners="OpenStreetMap, local city transit feeds, truck sensor manufacturers.",
            cost_structure="Mapping server hosting, server instances, sales representatives.",
            first_validation="Implement optimized route suggestions for 15 delivery trucks and compare to baseline routes."
        )

        # Connect evidence to the respective chunks for all 3 opportunities
        cls._create_opp_evidences(db, company.id, opp1, opp2, opp3)

        # Step 6: Ranking and Completion
        ProcessingJobRepository.update(db, job_id, current_step="06 Ranking Results", progress=100.0, status="completed")
        logger.info("FrostLink demo data loaded successfully.")
        
        # Connect capabilities/problems to opportunities in knowledge graph
        GraphService.add_node(opp1.id, "Opportunity", {"name": opp1.title, "score": opp1.overall_score})
        GraphService.add_node(opp2.id, "Opportunity", {"name": opp2.title, "score": opp2.overall_score})
        GraphService.add_node(opp3.id, "Opportunity", {"name": opp3.title, "score": opp3.overall_score})
        
        GraphService.add_relationship("realtime_iot", opp1.id, "ENABLES")
        GraphService.add_relationship("temp_anomaly", opp1.id, "INSPIRES")
        GraphService.add_relationship("spoilage_risk", opp1.id, "INSPIRES")
        GraphService.add_relationship("c9_compressor", opp2.id, "INSPIRES")
        GraphService.add_relationship("fleet_routes", opp3.id, "INSPIRES")

        return company

    @staticmethod
    def _create_opp_evidences(db: Session, company_id: str, opp1, opp2, opp3):
        """
        Query database chunks and associate them to opportunities with a semantic score.
        """
        # Fetch the assets we created
        assets = db.query(Asset).filter(Asset.company_id == company_id).all()
        asset_map = {a.file_name: a for a in assets}
        
        # Opp 1: Cold Chain Intelligence evidence
        # Links: operations report, temp anomalies, complaints
        if "logistics_operations_report.txt" in asset_map:
            rep = asset_map["logistics_operations_report.txt"]
            chunks = AssetRepository.get_chunks_by_asset(db, rep.id)
            if chunks:
                OpportunityRepository.create_evidence(
                    db=db,
                    opportunity_id=opp1.id,
                    chunk_id=chunks[0].id,
                    asset_id=rep.id,
                    relevance_score=0.92,
                    supporting_text="Our GPS telemetry shows Route 101 and Route 5 suffer from heavy traffic delays. On Route 101, transit times have increased... chilling compressors fail to maintain 2.0°C during extended gridlocks."
                )
                
        if "warehouse_temp_anomalies.csv" in asset_map:
            anom = asset_map["warehouse_temp_anomalies.csv"]
            chunks = AssetRepository.get_chunks_by_asset(db, anom.id)
            if chunks:
                OpportunityRepository.create_evidence(
                    db=db,
                    opportunity_id=opp1.id,
                    chunk_id=chunks[0].id,
                    asset_id=anom.id,
                    relevance_score=0.88,
                    supporting_text="SEN-ROOM3-1 Temperature anomaly drift detected: 4.8°C at 08:00, spiking to 7.8°C at 16:00."
                )

        if "customer_complaints.csv" in asset_map:
            comp = asset_map["customer_complaints.csv"]
            chunks = AssetRepository.get_chunks_by_asset(db, comp.id)
            if chunks:
                OpportunityRepository.create_evidence(
                    db=db,
                    opportunity_id=opp1.id,
                    chunk_id=chunks[0].id,
                    asset_id=comp.id,
                    relevance_score=0.95,
                    supporting_text="MediSave Pharma vaccine batch rejected (delivered at 7.5°C). FreshFoods Market reports fish decay due to refrigeration drift at 6.8°C."
                )

        # Opp 2: Predictive Maintenance evidence
        # Links: equipment audit, complaints
        if "refrigeration_equipment_audit.txt" in asset_map:
            aud = asset_map["refrigeration_equipment_audit.txt"]
            chunks = AssetRepository.get_chunks_by_asset(db, aud.id)
            if chunks:
                OpportunityRepository.create_evidence(
                    db=db,
                    opportunity_id=opp2.id,
                    chunk_id=chunks[0].id,
                    asset_id=aud.id,
                    relevance_score=0.94,
                    supporting_text="Compressor C-9 has signs of electrical amperage fluctuations and abnormal vibration. In July, Room 3 experienced a 4-hour temperature spike from 1.5°C to 7.8°C due to downtime."
                )
                
        # Opp 3: Logistics Optimization AI evidence
        # Links: operations report
        if "logistics_operations_report.txt" in asset_map:
            rep = asset_map["logistics_operations_report.txt"]
            chunks = AssetRepository.get_chunks_by_asset(db, rep.id)
            if chunks:
                OpportunityRepository.create_evidence(
                    db=db,
                    opportunity_id=opp3.id,
                    chunk_id=chunks[0].id,
                    asset_id=rep.id,
                    relevance_score=0.86,
                    supporting_text="Route 101 transit times have increased by an average of 45 minutes... compressors fail to maintain target temperature during extended gridlocks."
                )
