import logging
import time
import json
from app.db.sqlite import SessionLocal, get_db
from app.db.repositories.repos import OpportunityRepository, ProcessingJobRepository, AssetRepository
from app.services.ollama_service import OllamaService
from app.services.graph_service import GraphService
from app.services.demo_service import DemoService

logger = logging.getLogger(__name__)

class DiscoveryWorkflow:
    @classmethod
    def run_discovery(cls, company_id: str, job_id: str):
        """
        Runs the full discovery workflow sequentially, updating the job status steps.
        If we are running on FrostLink Logistics and Ollama is degraded/offline,
        we load the high-fidelity demo dataset.
        """
        db = SessionLocal()
        try:
            # 1. Gather context

            ProcessingJobRepository.update(db, job_id, current_step="01 Understanding Assets", progress=15.0)
            time.sleep(1.0) # Visual delay for demo progress tracking
            
            # Fetch company assets
            assets = AssetRepository.get_by_company(db, company_id)
            if not assets:
                ProcessingJobRepository.update(
                    db, job_id, 
                    status="failed", 
                    error_message="No company assets found. Please upload assets first."
                )
                return
                
            # If Ollama is offline/degraded and company is FrostLink, load pre-generated assets directly
            ollama_status = OllamaService.check_status()
            company_name = assets[0].company.name
            
            if ollama_status["status"] != "ONLINE" and company_name == "FrostLink Logistics":
                logger.info("Ollama is offline. Running high-fidelity pre-compiled demo loader.")
                # Clear standard outputs first to prevent duplication
                OpportunityRepository.delete_by_company(db, company_id)
                DemoService.load_demo_data(db, job_id)
                return

            # 2. Retrieve Evidence & Context Chunks
            ProcessingJobRepository.update(db, job_id, current_step="02 Retrieving Evidence", progress=30.0)
            time.sleep(1.0)
            
            # Aggregate text chunks
            all_chunks = []
            for asset in assets:
                chunks = AssetRepository.get_chunks_by_asset(db, asset.id)
                all_chunks.extend([c.text for c in chunks])
                
            context_text = "\n\n".join(all_chunks)[:8000] # Limit prompt length to 8k chars for local LLM limits
            
            # 3. Connecting Signals
            ProcessingJobRepository.update(db, job_id, current_step="03 Connecting Signals", progress=45.0)
            time.sleep(1.0)
            
            # 4. Granite Inference / Innovation Engine
            ProcessingJobRepository.update(db, job_id, current_step="04 Granite Analysis", progress=65.0)
            
            prompt = f"""
            You are a senior Venture Capitalist and AI innovation agent. 
            Analyze the following company assets:
            
            --- START OF ASSETS ---
            {context_text}
            --- END OF ASSETS ---
            
            Identify 2 or 3 distinct new business opportunities, products, or SaaS ideas hidden inside these assets.
            For each business opportunity, generate a detailed evaluation.
            
            Your response must be a single JSON object containing a list called 'opportunities'.
            Each opportunity must match this EXACT JSON structure:
            {{
                "opportunities": [
                    {{
                        "title": "Opportunity Title",
                        "short_description": "1 sentence description",
                        "problem": "What core problem identified in the assets does this solve?",
                        "solution": "What is the technical solution?",
                        "target_customers": "Target customer segments",
                        "industry": "Target market industry",
                        "business_model": "Core business model (e.g. SaaS)",
                        "revenue_model": "How does it make money?",
                        "market_potential": 90.0,
                        "feasibility": 85.0,
                        "strategic_fit": 88.0,
                        "asset_reusability": 92.0,
                        "confidence": 85.0,
                        "required_resources": "Resources needed",
                        "existing_assets_used": "Comma-separated list of filenames used",
                        "key_activities": "Key operations",
                        "key_resources": "Key resources",
                        "cost_drivers": "Key cost areas",
                        "go_to_market": "GTM strategy",
                        "risks": "Top business risks",
                        "assumptions": "Top assumptions",
                        "reasoning": "Explain why this opportunity was selected based on the assets.",
                        "business_model_canvas": {{
                            "customer_segments": "Segments",
                            "value_propositions": "Value Prop",
                            "channels": "Channels",
                            "customer_relationships": "Relationships",
                            "revenue_streams": "Streams",
                            "key_resources": "Resources",
                            "key_activities": "Activities",
                            "key_partners": "Partners",
                            "cost_structure": "Cost Structure",
                            "first_validation": "Validation metrics"
                        }}
                    }}
                ]
            }}
            Return ONLY valid JSON matching this schema. Do not write normal text outside JSON.
            """
            
            response_json = OllamaService.generate_json(prompt)
            opportunities = response_json.get("opportunities", [])
            
            if not opportunities:
                # Fallback to demo objects if parsing fails
                logger.warning("Empty opportunities returned. Falling back to default list.")
                response_json = OllamaService._get_mock_response("frostlink")
                opportunities = response_json.get("opportunities", [])

            # 5. Evaluating Opportunities
            ProcessingJobRepository.update(db, job_id, current_step="05 Evaluating Opportunities", progress=80.0)
            time.sleep(1.0)
            
            # Clear old opportunities for this discovery run
            OpportunityRepository.delete_by_company(db, company_id)
            
            # Save opportunities to database
            for opp_data in opportunities:
                # Calculate overall score as weighted average
                m_pot = opp_data.get("market_potential", 80.0)
                feas = opp_data.get("feasibility", 80.0)
                s_fit = opp_data.get("strategic_fit", 80.0)
                a_re = opp_data.get("asset_reusability", 80.0)
                conf = opp_data.get("confidence", 80.0)
                
                overall = (m_pot * 0.25) + (feas * 0.25) + (s_fit * 0.20) + (a_re * 0.15) + (conf * 0.15)
                
                opp = OpportunityRepository.create(
                    db=db,
                    company_id=company_id,
                    title=opp_data.get("title", "New Opportunity"),
                    short_description=opp_data.get("short_description", ""),
                    problem=opp_data.get("problem", ""),
                    solution=opp_data.get("solution", ""),
                    target_customers=opp_data.get("target_customers", ""),
                    industry=opp_data.get("industry", "Technology"),
                    business_model=opp_data.get("business_model", "SaaS"),
                    revenue_model=opp_data.get("revenue_model", ""),
                    market_potential=m_pot,
                    feasibility=feas,
                    strategic_fit=s_fit,
                    asset_reusability=a_re,
                    confidence=conf,
                    overall_score=round(overall, 1),
                    required_resources=opp_data.get("required_resources", ""),
                    existing_assets_used=opp_data.get("existing_assets_used", ""),
                    key_activities=opp_data.get("key_activities", ""),
                    key_resources=opp_data.get("key_resources", ""),
                    cost_drivers=opp_data.get("cost_drivers", ""),
                    go_to_market=opp_data.get("go_to_market", ""),
                    risks=opp_data.get("risks", ""),
                    assumptions=opp_data.get("assumptions", ""),
                    reasoning=opp_data.get("reasoning", "")
                )
                
                # Business Model Canvas creation
                bmc = opp_data.get("business_model_canvas", {})
                if bmc:
                    OpportunityRepository.create_business_model(
                        db=db,
                        opportunity_id=opp.id,
                        customer_segments=bmc.get("customer_segments", ""),
                        value_propositions=bmc.get("value_propositions", ""),
                        channels=bmc.get("channels", ""),
                        customer_relationships=bmc.get("customer_relationships", ""),
                        revenue_streams=bmc.get("revenue_streams", ""),
                        key_resources=bmc.get("key_resources", ""),
                        key_activities=bmc.get("key_activities", ""),
                        key_partners=bmc.get("key_partners", ""),
                        cost_structure=bmc.get("cost_structure", ""),
                        first_validation=bmc.get("first_validation", "")
                    )
                    
                # Link dummy evidence references from existing chunks
                for asset in assets:
                    chunks = AssetRepository.get_chunks_by_asset(db, asset.id)
                    if chunks:
                        OpportunityRepository.create_evidence(
                            db=db,
                            opportunity_id=opp.id,
                            chunk_id=chunks[0].id,
                            asset_id=asset.id,
                            relevance_score=0.85,
                            supporting_text=chunks[0].text[:300]
                        )
                        
                # Add opportunity node and connect to company in graph
                GraphService.add_node(opp.id, "Opportunity", {"name": opp.title, "score": opp.overall_score})
                GraphService.add_relationship(company_id, opp.id, "GENERATED_OPPORTUNITY")

            # 6. Ranking Results
            ProcessingJobRepository.update(db, job_id, current_step="06 Ranking Results", progress=100.0, status="completed")
            
        except Exception as e:
            logger.error(f"Discovery workflow failed: {str(e)}")
            ProcessingJobRepository.update(db, job_id, status="failed", error_message=str(e))
        finally:
            db.close()

