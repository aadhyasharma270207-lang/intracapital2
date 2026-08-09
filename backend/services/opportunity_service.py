import uuid
from backend import config
from backend import scoring
from backend.services.granite_service import GraniteService
from backend.services.rag_service import retrieve_evidence

# Fictional company dataset backup (Demo mode default)
DEMO_OPPORTUNITIES = [
    {
        "id": "opp_cold_chain_1",
        "name": "Cold Chain Intelligence Platform",
        "pitch": "A real-time, pallet-level thermal tracking and predictive spoilage monitoring system using wireless mesh sensor beacons.",
        "problem": "Customers report $14,000 losses in organic berries (SH-1082) and $85,000 write-offs in biologics (SH-1104) due to microclimate temperature spikes that aggregate container-level sensors fail to detect.",
        "solution": "Deploy patented Low-Power Wireless Mesh Beacons (PAT-US-10492811-B2) at the individual pallet level, combined with the R&D team's thermal stress integral degradation model (RD-2025-99) to predict remaining shelf-life in real-time, sending alerts or triggering route changes before spoilage occurs.",
        "existing_assets": [
            "Patent PAT-US-10492811-B2 (Wireless Mesh Beacon)",
            "Research Document RD-2025-99 (Thermal Stress Spoilage Model)"
        ],
        "asset_connection": "Integrates our proprietary low-power wireless mesh sensing technology (PAT-US-10492811-B2) with the R&D thermal stress calculations (RD-2025-99) to analyze pallet microclimates.",
        "target_customers": [
            "Pharmaceutical Logistics Managers",
            "Organic Produce Distributors",
            "Premium Seafood Exporters"
        ],
        "revenue_model": "SaaS platform fee based on shipment volume + hardware sensor leasing.",
        "market_potential": 92.0,
        "feasibility": 88.0,
        "strategic_fit": 95.0,
        "asset_reusability": 90.0,
        "confidence": 95.0,
        "evidence": [
            "patents.txt: Patent PAT-US-10492811-B2 low-power sensor beacon",
            "research_report.txt: Document RD-2025-99 thermal stress integrals",
            "customer_feedback.txt: Log CF-2026-042 insulin $85,000 loss"
        ],
        "reasoning": "Direct match between active customer financial write-offs and patented, researched corporate assets that can be productized immediately.",
        "implementation_difficulty": "Medium",
        "expected_business_impact": "High cost savings by reducing cold chain write-offs by 90%",
        "key_risks": ["Radio signal attenuation through dense cargo boxes", "Calibrating temperature sensors across extreme ranges"],
        "recommended_next_experiment": "Deploy 5 mesh beacons in a pilot run containing organic strawberries over a 15-mile transit."
    },
    {
        "id": "opp_pred_maint_2",
        "name": "Predictive Equipment Maintenance",
        "pitch": "A machine learning predictive maintenance service for industrial cooling compressors based on acoustic wave signatures.",
        "problem": "Sudden mechanical failures in warehouse compressors (Warehouse WH-101 Comp-A seized on July 14, causing Zone 3 cooling power-down and thermal spikes) and transit cooling units result in cargo losses and high emergency repair costs.",
        "solution": "Attach vibration sensors to compressor shafts to capture acoustic waveforms, analyzing them with the internal ML algorithm (RD-2025-102) and edge detector patent (PAT-US-11029302-B1) to predict bearing failure 7 to 10 days in advance.",
        "existing_assets": [
            "Patent PAT-US-11029302-B1 (Acoustic Rotary wave detector)",
            "Research Document RD-2025-102 (ML Compressor Wear Model)"
        ],
        "asset_connection": "Pairs acoustic signature analysis edge patent (PAT-US-11029302-B1) with internal compressor ML predictive code (RD-2025-102) to monitor warehouse and container refrigeration hardware.",
        "target_customers": [
            "Cold Storage Facility Operators",
            "Refrigerated Shipping Container Fleets",
            "Industrial Refrigeration OEMs"
        ],
        "revenue_model": "Predictive maintenance licensing and subscription dashboard per cooling unit.",
        "market_potential": 85.0,
        "feasibility": 80.0,
        "strategic_fit": 85.0,
        "asset_reusability": 85.0,
        "confidence": 90.0,
        "evidence": [
            "patents.txt: Patent PAT-US-11029302-B1 wave anomaly detector",
            "research_report.txt: Document RD-2025-102 ML compressor wear prediction",
            "operations_report.txt: Facilities status Comp-A seized July 14"
        ],
        "reasoning": "Leverages internal edge diagnostics and ML code to solve recurring facilities breakdowns, saving emergency maintenance costs and preventing warehouse cargo exposures.",
        "implementation_difficulty": "High",
        "expected_business_impact": "Prevents catastrophic facilities shutdowns and decreases unplanned downtime by 40%",
        "key_risks": ["High ambient warehouse acoustic noise filtering", "Edge microcontrollers hardware processing limits"],
        "recommended_next_experiment": "Record compressor sound waveforms during normal and failing operations on one facility unit."
    },
    {
        "id": "opp_log_risk_3",
        "name": "Logistics Risk Intelligence",
        "pitch": "A weather-aware dynamic routing engine that predicts and mitigates shipment delays and environmental cargo exposure risks.",
        "problem": "Logistics runs on static schedules, ignoring storm warnings or harbor congestion, leading to prolonged delays (e.g. SH-1051 delayed 18 hours in Richmond storm, SH-1066 delayed 22 hours at Newark yard) which drain battery backups and cause cargo damage.",
        "solution": "Build a dynamic route risk engine integrating weather forecasts, port traffic, and transit telemetry to optimize dispatch schedules, rerouting shipments around severe weather (e.g., Richmond, VA) or port bottlenecks.",
        "existing_assets": [
            "Operations Reports (Static routing audit)",
            "Logistics Reports (Shipment SH-1051 Richmond delay history)"
        ],
        "asset_connection": "Correlates historic shipment logs (SH-1051 weather delay, SH-1112 Route 70 construction) with sensor data coordinates to train weather-aware risk algorithms.",
        "target_customers": [
            "Freight Forwarders",
            "High-Value Fleet Operators",
            "Supply Chain Insurance Underwriters"
        ],
        "revenue_model": "SaaS routing API usage and dynamic dashboard subscriptions.",
        "market_potential": 80.0,
        "feasibility": 75.0,
        "strategic_fit": 80.0,
        "asset_reusability": 70.0,
        "confidence": 85.0,
        "evidence": [
            "logistics_report.txt: Shipment SH-1051 delayed 18 hours near Richmond storm",
            "operations_report.txt: static schedule bottlenecks and battery strain logs"
        ],
        "reasoning": "Improves route reliability scores by applying historical delay analytics to dynamic scheduling, preventing cargo container battery backup depletion.",
        "implementation_difficulty": "Low",
        "expected_business_impact": "Reduces fuel consumption and weather-related delays by 25%",
        "key_risks": ["Real-time meteorological API lag", "GPS coordinate inaccuracies in heavy storms"],
        "recommended_next_experiment": "Create a pilot weather-routing algorithm and compare paths against historical Richmond delay logs."
    }
]

# Business model canvases for the opportunities
DEMO_CANVAS = {
    "opp_cold_chain_1": {
        "target_customer": "Perishable food growers, pharma laboratories, vaccine distributors.",
        "value_proposition": "Continuous shelf-life validation utilizing microclimate indicators at pallet levels.",
        "revenue_model": "Hardware leases plus monthly platform SaaS subscription fees.",
        "distribution": "Direct sales to pharmaceutical logistics managers and retail cold storage directors.",
        "key_resources": "Proprietary wireless beacon mesh patent, food degradation algorithm, cloud analytics.",
        "key_activities": "Beacon deployment, algorithm refinement, temperature alarm alerts integration.",
        "cost_drivers": "Beacon assembly, server hosting, direct customer support.",
        "go_to_market": "Partner with a mid-sized regional biologics distributor to run a 3-month proof of concept.",
        "first_validation_experiment": "Deploy beacons in 5 vaccine shipments, comparing shelf-life prediction accuracy against physical quality indicators.",
        "labels": {
            "target_customer": "Evidence-backed",
            "value_proposition": "Evidence-backed",
            "revenue_model": "AI-generated hypothesis",
            "distribution": "Requires validation",
            "key_resources": "Evidence-backed",
            "key_activities": "AI-generated hypothesis",
            "cost_drivers": "Requires validation",
            "go_to_market": "Requires validation",
            "first_validation_experiment": "Requires validation"
        }
    },
    "opp_pred_maint_2": {
        "target_customer": "Automated warehouse facilities, cold storage hubs.",
        "value_proposition": "Acoustic motor waveform diagnostics preventing cooling compressor seized failure.",
        "revenue_model": "Annual licensing fee per monitored compressor unit.",
        "distribution": "Refrigeration equipment distributors and industrial facilities management agencies.",
        "key_resources": "Rotary equipment wave anomaly detector patent, ML bearing prediction libraries.",
        "key_activities": "Shaft sensor mounting, real-time waveform anomaly dashboard alerts.",
        "cost_drivers": "Vibration sensors, model calibration, emergency support.",
        "go_to_market": "Direct campaign targeting HVAC leads at the top 10 retail distribution centers.",
        "first_validation_experiment": "Instrument 3 warehouse compressors, verify motor winding warning alerts against manual physical check inspection.",
        "labels": {
            "target_customer": "Evidence-backed",
            "value_proposition": "Evidence-backed",
            "revenue_model": "AI-generated hypothesis",
            "distribution": "Requires validation",
            "key_resources": "Evidence-backed",
            "key_activities": "AI-generated hypothesis",
            "cost_drivers": "Requires validation",
            "go_to_market": "Requires validation",
            "first_validation_experiment": "Requires validation"
        }
    },
    "opp_log_risk_3": {
        "target_customer": "High-value cold fleet operations, dry ice shipments handlers.",
        "value_proposition": "Dynamic weather-aware dispatch scheduler preventing generator runout delays.",
        "revenue_model": "Tiered SaaS API model charged per transit route dispatch.",
        "distribution": "Integration into existing enterprise Transport Management Systems (TMS).",
        "key_resources": "Historical route congestion logs, weather integration APIs.",
        "key_activities": "Route hazard model training, custom weather feed integration.",
        "cost_drivers": "Mapping API usage, predictive route computing costs.",
        "go_to_market": "Offer free integration plugins for logistics management platforms.",
        "first_validation_experiment": "Track 20 shipments using static dispatch and 20 shipments using dynamic route advisory, measuring route reliability.",
        "labels": {
            "target_customer": "Evidence-backed",
            "value_proposition": "Evidence-backed",
            "revenue_model": "AI-generated hypothesis",
            "distribution": "Requires validation",
            "key_resources": "Evidence-backed",
            "key_activities": "AI-generated hypothesis",
            "cost_drivers": "Requires validation",
            "go_to_market": "Requires validation",
            "first_validation_experiment": "Requires validation"
        }
    }
}

class OpportunityService:
    def __init__(self):
        self.granite = GraniteService()
        self.active_opportunities = []
        
    def get_opportunities(self) -> list:
        """
        Returns currently loaded opportunities. Defaults to demo data if none exist.
        """
        if not self.active_opportunities:
            # Populate with scored demo opportunities
            self.active_opportunities = scoring.score_and_rank_opportunities(DEMO_OPPORTUNITIES)
        return self.active_opportunities

    def reset(self):
        """
        Clears cached state.
        """
        self.active_opportunities = []

    def discover_opportunities(self, evidence: list = None) -> list:
        """
        Runs the multi-stage Venture Discovery Pipeline:
          Stage 1: Asset understanding
          Stage 2: Cross-domain connection discovery
          Stage 3: Opportunity generation
          Stage 4: Quality evaluation (filtering)
          Stage 5: Python scoring & ranking
        """
        # If no evidence retrieved, default to fallback immediately
        if not evidence:
            print("[OPPORTUNITY SERVICE] No evidence provided. Defaulting to Demo Mode.")
            self.active_opportunities = scoring.score_and_rank_opportunities(DEMO_OPPORTUNITIES)
            return self.active_opportunities

        # Check if live Granite connection is active
        if not self.granite.is_configured:
            print("[OPPORTUNITY SERVICE] Watsonx credentials missing. Defaulting to Demo Mode.")
            self.active_opportunities = scoring.score_and_rank_opportunities(DEMO_OPPORTUNITIES)
            return self.active_opportunities

        # Compile evidence context
        evidence_context = "\n\n".join([
            f"Source Document: {item['filename']} (Page: {item.get('page', 'N/A')}, Relevance: {item.get('relevance', 'unknown')}%)\nSnippet:\n{item['text']}"
            for item in evidence
        ])

        system_prompt = (
            "You are INTRACAPITAL, a premium AI Venture Discovery Engine. Your task is to analyze "
            "the provided corporate evidence (patents, research, telemetry summaries, operations reports) "
            "and discover exactly 3-5 high-potential business opportunities that can be launched "
            "by leveraging and combining these existing assets. "
            "You must return your output strictly in JSON format. Do not write conversational introductions or markdown headers outside the JSON block."
        )

        prompt = f"""
Analyze the corporate evidence below. Discover between 3 and 5 distinct new business opportunities.
Each opportunity must link at least one technology asset (e.g. a patent or research paper) with a business pain point (e.g., customer complaints, operational failures, or telemetry excursions).

Corporate Evidence:
\"\"\"
{evidence_context}
\"\"\"

Return a JSON array under the key "opportunities". Each opportunity must contain these exact fields:
- name: string (Venture name)
- pitch: string (One-line pitch / business thesis)
- problem: string (Grounded in customer complaints or operational failures from evidence)
- solution: string (How we solve it using our technology assets)
- existing_assets: array of strings (Specific patent titles or research report refs referenced in evidence)
- asset_connection: string (How the assets correlate together to form this opportunity)
- target_customers: array of strings
- revenue_model: string
- market_potential: number (0-100 score)
- feasibility: number (0-100 score)
- strategic_fit: number (0-100 score)
- asset_reusability: number (0-100 score)
- confidence: number (0-100 score)
- reasoning: string (Concise explanation of the commercial opportunity)
- evidence: array of strings (Direct references to sources in evidence, e.g. "customer_feedback.txt log CF-2026-001 and patents.txt Patent PAT-US-10492811-B2")
- implementation_difficulty: string (either "High", "Medium", or "Low")
- expected_business_impact: string (commercial impact description)
- key_risks: array of strings (primary operational/business risks)
- recommended_next_experiment: string (first validation experiment to run)

Ensure all names and descriptions correspond strictly to the evidence. Do not invent any patents or assets not explicitly listed in the evidence.

JSON Schema format:
{{
  "opportunities": [
     {{
       "name": "...",
       "pitch": "...",
       "problem": "...",
       "solution": "...",
       "existing_assets": ["..."],
       "asset_connection": "...",
       "target_customers": ["..."],
       "revenue_model": "...",
       "market_potential": 85,
       "feasibility": 75,
       "strategic_fit": 80,
       "asset_reusability": 70,
       "confidence": 85,
       "reasoning": "...",
       "evidence": ["..."],
       "implementation_difficulty": "Medium",
       "expected_business_impact": "...",
       "key_risks": ["..."],
       "recommended_next_experiment": "..."
     }}
  ]
}}
"""

        try:
            response = self.granite.generate_json(prompt, system_prompt)
            opp_list = response.get("opportunities", [])
            
            # Quality Control Filter
            validated_list = []
            for opp in opp_list:
                # 1. Required keys check
                required_keys = [
                    "name", "pitch", "problem", "solution", "existing_assets", "asset_connection", 
                    "target_customers", "revenue_model", "market_potential", "feasibility", "strategic_fit", 
                    "asset_reusability", "confidence", "reasoning", "evidence", "implementation_difficulty", 
                    "expected_business_impact", "key_risks", "recommended_next_experiment"
                ]
                if not all(k in opp for k in required_keys):
                    continue
                    
                # 2. Score limits check (0-100)
                opp["market_potential"] = max(0.0, min(100.0, float(opp["market_potential"])))
                opp["feasibility"] = max(0.0, min(100.0, float(opp["feasibility"])))
                opp["strategic_fit"] = max(0.0, min(100.0, float(opp["strategic_fit"])))
                opp["asset_reusability"] = max(0.0, min(100.0, float(opp["asset_reusability"])))
                opp["confidence"] = max(0.0, min(100.0, float(opp["confidence"])))
                
                # 3. Evidence links existence check
                if not opp["evidence"] or not opp["existing_assets"]:
                    continue
                    
                # Assign short ID
                opp["id"] = f"opp_{uuid.uuid4().hex[:8]}"
                validated_list.append(opp)
                
            # Restrict to maximum 5
            validated_list = validated_list[:5]
            
            if len(validated_list) == 0:
                raise ValueError("No generated opportunities passed validation requirements.")
                
            # Score and rank
            self.active_opportunities = scoring.score_and_rank_opportunities(validated_list)
            return self.active_opportunities

        except Exception as e:
            print(f"[OPPORTUNITY SERVICE] Pipeline execution failed: {e}. Falling back to Demo Mode.")
            self.active_opportunities = scoring.score_and_rank_opportunities(DEMO_OPPORTUNITIES)
            return self.active_opportunities

    def generate_business_model(self, opp_id: str) -> dict:
        """
        Generates/fetches the Business Model canvas details.
        Uses Granite prompt expansion when live credentials exist, falling back to preconfigured stubs.
        """
        # If in Demo Mode or if opp_id is in demo keys, check if demo canvas exists
        if opp_id in DEMO_CANVAS:
            return DEMO_CANVAS[opp_id]
            
        # Get active opportunity
        active_opp = None
        for opp in self.active_opportunities:
            if opp.get("id") == opp_id:
                active_opp = opp
                break
                
        if not active_opp:
            # Fallback to first demo canvas
            return DEMO_CANVAS["opp_cold_chain_1"]

        # If watsonx is not configured, return a default mock canvas based on active_opp properties
        if not self.granite.is_configured:
            return {
                "target_customer": ", ".join(active_opp.get("target_customers", [])),
                "value_proposition": active_opp.get("pitch", ""),
                "revenue_model": active_opp.get("revenue_model", ""),
                "distribution": "⚠️ Requires validation (No direct evidence in assets)",
                "key_resources": ", ".join(active_opp.get("existing_assets", [])),
                "key_activities": "⚠️ Requires validation (Core activities must be defined)",
                "cost_drivers": "⚠️ Requires validation (Needs cost calculations)",
                "go_to_market": "⚠️ Requires validation (Requires launch strategies)",
                "first_validation_experiment": "⚠️ Requires validation (Needs prototype validation plan)",
                "labels": {
                    "target_customer": "Evidence-backed",
                    "value_proposition": "Evidence-backed",
                    "revenue_model": "AI-generated hypothesis",
                    "distribution": "Requires validation",
                    "key_resources": "Evidence-backed",
                    "key_activities": "Requires validation",
                    "cost_drivers": "Requires validation",
                    "go_to_market": "Requires validation",
                    "first_validation_experiment": "Requires validation"
                }
            }

        # Prompt Granite to expand the business canvas
        system_prompt = (
            "You are a Senior Venture Architect. Expand the provided business opportunity into a "
            "structured business model canvas. Your output must be returned strictly in JSON format."
        )

        prompt = f"""
Expand this venture opportunity into a detailed Business Model Canvas:
Venture Name: {active_opp.get('name')}
Pitch: {active_opp.get('pitch')}
Problem: {active_opp.get('problem')}
Solution: {active_opp.get('solution')}
Existing Assets: {', '.join(active_opp.get('existing_assets', []))}

Generate the following canvas blocks. Identify if they are "Evidence-backed" (grounded in the files/patents), "AI-generated hypothesis" (logical extrapolation), or "Requires validation" (needs external field testing).

Return a JSON object with these exact keys:
- target_customer: string
- value_proposition: string
- revenue_model: string
- distribution: string
- key_resources: string
- key_activities: string
- cost_drivers: string
- go_to_market: string
- first_validation_experiment: string
- labels: object containing keys matching the above field names, with values of either "Evidence-backed", "AI-generated hypothesis", or "Requires validation"

JSON Schema output:
{{
  "target_customer": "...",
  "value_proposition": "...",
  "revenue_model": "...",
  "distribution": "...",
  "key_resources": "...",
  "key_activities": "...",
  "cost_drivers": "...",
  "go_to_market": "...",
  "first_validation_experiment": "...",
  "labels": {{
    "target_customer": "Evidence-backed",
    "value_proposition": "Evidence-backed",
    "revenue_model": "AI-generated hypothesis",
    ...
  }}
}}
"""
        try:
            res_dict = self.granite.generate_json(prompt, system_prompt)
            # Ensure opportunity_id is added
            res_dict["opportunity_id"] = opp_id
            return res_dict
        except Exception as e:
            print(f"[OPPORTUNITY SERVICE] Failed to expand canvas via Granite: {e}")
            # Return basic mock
            return {
                "target_customer": ", ".join(active_opp.get("target_customers", [])),
                "value_proposition": active_opp.get("pitch", ""),
                "revenue_model": active_opp.get("revenue_model", ""),
                "distribution": "⚠️ Requires validation",
                "key_resources": ", ".join(active_opp.get("existing_assets", [])),
                "key_activities": "⚠️ Requires validation",
                "cost_drivers": "⚠️ Requires validation",
                "go_to_market": "⚠️ Requires validation",
                "first_validation_experiment": "⚠️ Requires validation",
                "labels": {
                    "target_customer": "Evidence-backed",
                    "value_proposition": "Evidence-backed",
                    "revenue_model": "AI-generated hypothesis",
                    "distribution": "Requires validation",
                    "key_resources": "Evidence-backed",
                    "key_activities": "Requires validation",
                    "cost_drivers": "Requires validation",
                    "go_to_market": "Requires validation",
                    "first_validation_experiment": "Requires validation"
                }
            }
