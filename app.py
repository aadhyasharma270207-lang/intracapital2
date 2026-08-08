import streamlit as st
import pandas as pd
from pathlib import Path
import httpx
import os
import plotly.express as px

# Set page configuration first
st.set_page_config(
    page_title="INTRACAPITAL | AI Venture Discovery Engine",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load helper constants
from backend import config
from frontend import styles
from frontend import components

# 1. Inject Visual Premium CSS
styles.inject_premium_styles()

# 2. Retrieve Internal key safely
FASTAPI_INTERNAL_API_KEY = ""
try:
    if hasattr(st, "secrets") and st.secrets is not None:
        if "FASTAPI_INTERNAL_API_KEY" in st.secrets:
            FASTAPI_INTERNAL_API_KEY = st.secrets["FASTAPI_INTERNAL_API_KEY"]
except Exception:
    pass

if not FASTAPI_INTERNAL_API_KEY:
    FASTAPI_INTERNAL_API_KEY = os.getenv("FASTAPI_INTERNAL_API_KEY", "")

# 3. HTTP Client Helper
def call_backend(method: str, endpoint: str, json_data: dict = None, files_data: list = None) -> dict:
    url = f"{config.FASTAPI_BASE_URL}{endpoint}"
    headers = {}
    if FASTAPI_INTERNAL_API_KEY:
        headers["Authorization"] = f"Bearer {FASTAPI_INTERNAL_API_KEY}"
        
    try:
        with httpx.Client(timeout=120.0) as client:
            if method.upper() == "GET":
                response = client.get(url, headers=headers)
            elif method.upper() == "POST":
                if files_data:
                    response = client.post(url, headers=headers, files=files_data)
                else:
                    response = client.post(url, headers=headers, json=json_data)
                    
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        try:
            err = e.response.json().get("detail", str(e))
        except Exception:
            err = e.response.text or str(e)
        return {"status": "error", "error": f"Backend Error: {err}"}
    except Exception as e:
        return {
            "status": "error", 
            "error": f"Cannot connect to FastAPI backend at {config.FASTAPI_BASE_URL}. Ensure uvicorn is running."
        }

# 4. Global Session State
if "opportunities" not in st.session_state:
    st.session_state.opportunities = []
if "evidence_used" not in st.session_state:
    st.session_state.evidence_used = []
if "pipeline_logs" not in st.session_state:
    st.session_state.pipeline_logs = []
if "pipeline_step" not in st.session_state:
    st.session_state.pipeline_step = "UPLOAD"
if "canvas_caches" not in st.session_state:
    st.session_state.canvas_caches = {}
if "validation_caches" not in st.session_state:
    st.session_state.validation_caches = {}

# 5. Sidebar Navigation Logo
st.sidebar.markdown(
    """
    <div style='text-align: left; padding: 10px 0 20px 0;'>
        <h2 style='margin:0; font-size: 1.8rem; background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: Outfit; font-weight: 800; letter-spacing: -0.02em;'>
            INTRACAPITAL
        </h2>
        <span style='font-size:0.7rem; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; display:block; margin-top:2px;'>AI VENTURE INTELLIGENCE</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation Menu", [
    "⌂ Overview",
    "◈ Company Assets",
    "◉ Discovery",
    "◆ Opportunities",
    "⌕ Evidence Explorer",
    "▣ Business Models",
    "◐ Validator",
    "⇄ Compare",
    "◫ Analytics",
    "⚙ Architecture",
    "● System"
])

# Quick Server health indicator in Sidebar footer
health_res = call_backend("GET", "/health")
is_fastapi_online = health_res.get("status") != "error"
granite_status = health_res.get("granite", "offline") if is_fastapi_online else "offline"
is_granite_live = granite_status == "online"

st.sidebar.markdown("---")
if is_fastapi_online:
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; color: #10b981; margin-bottom: 4px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#10b981; box-shadow:0 0 8px #10b981;"></span>
            FastAPI Backend Online
        </div>
        """, 
        unsafe_allow_html=True
    )
    if is_granite_live:
        st.sidebar.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; color: #10b981;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#10b981; box-shadow:0 0 8px #10b981;"></span>
                Live IBM Granite Active
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; color: #f59e0b;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#f59e0b; box-shadow:0 0 8px #f59e0b;"></span>
                Simulation Sandbox Mode
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; color: #f43f5e;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#f43f5e; box-shadow:0 0 8px #f43f5e;"></span>
            FastAPI Backend Offline
        </div>
        """, 
        unsafe_allow_html=True
    )

# ==========================================
# Page 1: ⌂ Overview
# ==========================================
if page == "⌂ Overview":
    components.render_home_hero(is_live=is_granite_live)
    
    # Fetch metrics
    metrics_res = call_backend("GET", "/metrics")
    if metrics_res.get("status") != "error":
        components.render_executive_dashboard(metrics_res, is_live=is_granite_live)
    else:
        st.error(metrics_res.get("error"))
        
    st.markdown("### System Subsystem Checks")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(
            "Use the status monitor to verify connectivity with Watsonx/Granite, ChromaDB, and local RAG modules."
        )
        if st.button("🧪 TEST AI CONNECTION", use_container_width=True):
            with st.spinner("Testing health pings to IBM watsonx.ai..."):
                health = call_backend("GET", "/health")
                if health.get("status") != "error":
                    if health.get("granite") == "online":
                        st.success("✅ IBM Granite Connected successfully! API credentials verified.")
                    else:
                        st.error("❌ IBM Granite Connection Failed. Using Sandbox Simulation Mode.")
                else:
                    st.error("❌ Health check endpoint unreachable.")
                    
    with col2:
        if is_fastapi_online:
            st.markdown(
                f"""
                <div style="background: rgba(11,16,36,0.6); border:1px solid rgba(56,189,248,0.1); border-radius:12px; padding:16px; font-size:0.85rem; color:#cbd5e1; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <b>Endpoint Port:</b> <code style="color:#38bdf8;">localhost:8080</code><br>
                    <b>Database Collections:</b> <code style="color:#38bdf8;">ChromaDB (Local)</code><br>
                    <b>Authentication Key:</b> <code style="color:#38bdf8;">{'CONFIGURED' if FASTAPI_INTERNAL_API_KEY else 'NONE'}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # Corporate Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 15px 0;">
            <strong style="color: #cbd5e1; font-family: Outfit;">INTRACAPITAL</strong> &nbsp;•&nbsp; AI Venture Intelligence Platform <br>
            <p style="margin-top: 4px; font-style: italic;">"AI-generated recommendations are evidence-grounded hypotheses and should be validated by human decision-makers."</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# Page 2: ◈ Company Assets
# ==========================================
elif page == "◈ Company Assets":
    st.markdown("## ◈ Company Assets Staging")
    st.write("Upload operations files, logistics reports, patents, and telemetry CSV datasets:")
    
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or CSV",
        type=["pdf", "txt", "csv"],
        accept_multiple_files=True
    )
    
    col_act1, col_act2, col_act3 = st.columns(3)
    with col_act1:
        if st.button("🚀 LOAD DEMO COMPANY DATA", use_container_width=True, type="primary"):
            with st.spinner("Copying fictional dataset into backend uploads..."):
                res = call_backend("POST", "/load-demo-data")
                if res.get("status") != "error":
                    st.success("Demo dataset loaded successfully!")
                    st.session_state.pipeline_step = "UPLOAD"
                    st.rerun()
                else:
                    st.error(res.get("error"))
                    
    with col_act2:
        if st.button("📤 UPLOAD AND STAGE FILES", use_container_width=True):
            if uploaded_files:
                files_payload = []
                for f in uploaded_files:
                    files_payload.append(("files", (f.name, f.read(), f.type)))
                with st.spinner("Uploading files to backend..."):
                    res = call_backend("POST", "/upload", files_data=files_payload)
                    if res.get("status") != "error":
                        st.success("Files uploaded. Staged for vector parsing.")
                        st.session_state.pipeline_step = "UPLOAD"
                    else:
                        st.error(res.get("error"))
            else:
                st.warning("Please select files to upload first, or click LOAD DEMO COMPANY DATA.")
                
    with col_act3:
        if st.button("🗑️ RESET ENVIRONMENT", use_container_width=True):
            with st.spinner("Resetting databases..."):
                res = call_backend("POST", "/reset")
                if res.get("status") != "error":
                    st.success("Environment reset complete.")
                    st.session_state.opportunities = []
                    st.session_state.evidence_used = []
                    st.session_state.canvas_caches = {}
                    st.session_state.validation_caches = {}
                    st.session_state.pipeline_step = "UPLOAD"
                    st.rerun()
                else:
                    st.error(res.get("error"))

    # Display staged files status
    st.markdown("### staged files list")
    metrics_res = call_backend("GET", "/metrics")
    if metrics_res.get("status") != "error":
        processed_count = metrics_res.get("documents_processed", 0)
        st.info(f"Staged corporate files: **{processed_count}** processed.")
    else:
        st.error(metrics_res.get("error"))

# ==========================================
# Page 3: ◉ Discovery
# ==========================================
elif page == "◉ Discovery":
    st.markdown("## ◉ Venture Discovery Console")
    st.write("Run the analysis pipeline and trigger the synthesis engine:")
    
    # 1. Ingestion Pipeline flow diagram
    st.markdown("### Data pipeline Indexing Flow")
    metrics_res = call_backend("GET", "/metrics")
    
    components.render_pipeline_flow(st.session_state.pipeline_step)
    
    col_pipe1, col_pipe2 = st.columns(2)
    with col_pipe1:
        if st.button("⚙️ RUN ANALYSIS PIPELINE", use_container_width=True):
            with st.spinner("Analyzing and indexing vector spaces..."):
                res = call_backend("POST", "/analyze")
                if res.get("status") != "error":
                    st.success(f"Analysis completed! {res.get('chunks_created')} chunks indexed.")
                    st.session_state.pipeline_step = "READY"
                else:
                    st.error(res.get("error"))
    with col_pipe2:
        discover_btn = st.button("🚀 DISCOVER HIDDEN BUSINESSES", use_container_width=True, type="primary")
        
    log_area = st.empty()
    
    if discover_btn:
        st.session_state.pipeline_logs = []
        
        def add_log(msg):
            st.session_state.pipeline_logs.append(msg)
            log_area.code("\n".join(st.session_state.pipeline_logs))
            
        add_log("[STAGE 01] UNDERSTANDING COMPANY ASSETS...")
        import time; time.sleep(0.4)
        
        add_log("[STAGE 02] RETRIEVING RELEVANT EVIDENCE CONTEXT...")
        time.sleep(0.4)
        
        add_log("[STAGE 03] CONNECTING HIDDEN SIGNALS...")
        time.sleep(0.4)
        
        add_log("[STAGE 04] CALLING IBM GRANITE ANALYSIS...")
        
        res = call_backend("POST", "/discover")
        if res.get("status") != "error":
            add_log("[STAGE 05] EVALUATING OPPORTUNITIES...")
            time.sleep(0.4)
            
            add_log("[STAGE 06] RANKING RESULTS... COMPLETE.")
            time.sleep(0.4)
            
            st.session_state.opportunities = res.get("opportunities", [])
            st.session_state.evidence_used = res.get("evidence_used", [])
            st.success("Venture discovery completed successfully! Switch to the '◆ Opportunities' tab to view results.")
        else:
            add_log(f"[API ERROR] {res.get('error')}")
            st.error("Engine execution encountered errors. Defaulting to Demo Mode fallback.")
            
            # Load fallback demo items
            res_fallback = call_backend("GET", "/opportunities")
            st.session_state.opportunities = res_fallback.get("opportunities", [])

# ==========================================
# Page 4: ◆ Opportunities
# ==========================================
elif page == "◆ Opportunities":
    st.markdown("## ◆ Surfaced opportunities")
    st.write("Browse and filter discoveries surfaced from corporate assets:")
    
    opps = st.session_state.opportunities
    if not opps:
        res_active = call_backend("GET", "/opportunities")
        opps = res_active.get("opportunities", [])
        st.session_state.opportunities = opps
        
    if opps:
        # Advanced Filtering Panel
        st.markdown("### 🎛️ Advanced Filtering")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            sectors = set()
            for opp in opps:
                for target in opp.get("target_customers", []):
                    sectors.add(target)
            selected_sectors = st.multiselect("Filter by Industry Sector", list(sectors), default=list(sectors))
            
        with col_f2:
            min_feasibility = st.slider("Filter by Min Feasibility Score (%)", 0, 100, 0)
            
        with col_f3:
            min_potential = st.slider("Filter by Min Market Potential (%)", 0, 100, 0)
            
        # Apply filters
        filtered_opps = []
        for opp in opps:
            if opp.get("feasibility", 0.0) < min_feasibility:
                continue
            if opp.get("market_potential", 0.0) < min_potential:
                continue
            if selected_sectors:
                opp_sectors = opp.get("target_customers", [])
                if not any(s in opp_sectors for s in selected_sectors):
                    continue
            filtered_opps.append(opp)
            
        st.markdown(f"Showing **{len(filtered_opps)}** of **{len(opps)}** opportunities:")
        
        for idx, opp in enumerate(filtered_opps):
            is_top = (idx == 0)
            components.render_opportunity_card(opp, rank=idx+1, is_top=is_top)
            
            # Drill-down expander
            opp_id = opp.get("id")
            with st.expander(f"🔍 Access Comprehensive Evidence & Drill-Down Insights for {opp.get('name')}"):
                # 1. Evidence Grounding
                st.markdown("#### 📜 Grounding Evidence Sources")
                evidence_list = st.session_state.evidence_used
                if not evidence_list:
                    # Fallback check
                    res_fallback = call_backend("POST", "/discover")
                    evidence_list = res_fallback.get("evidence_used", [])
                    st.session_state.evidence_used = evidence_list
                    
                assets_used = opp.get("existing_assets", [])
                relevant_chunks = [
                    c for c in evidence_list 
                    if any(asset.lower()[:15] in str(c.get("filename", "")).lower() for asset in assets_used)
                    or any(asset.lower()[:15] in str(c.get("text", "")).lower() for asset in assets_used)
                    or "feedback" in str(c.get("filename", "")).lower()
                ]
                if not relevant_chunks:
                    relevant_chunks = evidence_list[:2]
                    
                for chunk_idx, c in enumerate(relevant_chunks):
                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.2); border: 1px solid rgba(255,255,255,0.02); border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                            <span style="font-size:0.75rem; font-weight:600; color:#818cf8;">📜 Source: <code>{c.get('filename')}</code> (Relevance: {c.get('relevance', 80.0)}%)</span>
                            <p style="font-size:0.85rem; color:#cbd5e1; margin: 4px 0 0 0; font-style: italic;">"{c.get('text')[:300]}..."</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # 2. Business Model Canvas Drill-down
                st.markdown("#### 💼 Business Model Canvas Expansion")
                if opp_id in st.session_state.canvas_caches:
                    canvas = st.session_state.canvas_caches[opp_id]
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.markdown(f"🎯 **Customer Segment:** {canvas.get('target_customer')}")
                        st.markdown(f"💎 **Value Proposition:** {canvas.get('value_proposition')}")
                        st.markdown(f"💳 **Monetization Model:** {canvas.get('revenue_model')}")
                    with col_c2:
                        st.markdown(f"🔗 **Key Resources:** {canvas.get('key_resources')}")
                        st.markdown(f"⚙️ **Key Activities:** {canvas.get('key_activities')}")
                        st.markdown(f"🧪 **Validation Experiment:** {canvas.get('first_validation_experiment')}")
                else:
                    if st.button(f"Generate Canvas details for {opp.get('name')}", key=f"btn_canvas_{opp_id}"):
                        with st.spinner("Expanding canvas blocks via IBM Granite..."):
                            res_canvas = call_backend("POST", "/expand-business-model", json_data={"opportunity_id": opp_id})
                            if res_canvas.get("status") != "error":
                                st.session_state.canvas_caches[opp_id] = res_canvas
                                st.success("Canvas generated! Rerunning to load details...")
                                st.rerun()
                            else:
                                st.error(res_canvas.get("error"))
                                
                # 3. Decision metrics score explanation
                st.markdown("#### ⚖️ Transparent Scoring Breakdown")
                st.code(opp.get("score_explanation", ""))
    else:
        st.info("No venture discoveries currently loaded. Go to the assets tab or click discover.")

# ==========================================
# Page 5: ⌕ Evidence Explorer
# ==========================================
elif page == "⌕ Evidence Explorer":
    st.markdown("## ⌕ Evidence Explorer & Grounding Citations")
    
    opps = st.session_state.opportunities
    if not opps:
        res_active = call_backend("GET", "/opportunities")
        opps = res_active.get("opportunities", [])
        st.session_state.opportunities = opps
        
    if opps:
        opp_names = [o.get("name") for o in opps]
        selected_opp_name = st.selectbox("Select venture opportunity:", opp_names)
        
        idx = opp_names.index(selected_opp_name)
        selected_opp = opps[idx]
        
        # Load evidence used
        evidence_list = st.session_state.evidence_used
        if not evidence_list:
            res_pipeline = call_backend("POST", "/discover")
            evidence_list = res_pipeline.get("evidence_used", [])
            st.session_state.evidence_used = evidence_list
            
        # Renders the 3D-inspired SVG node network map
        components.render_opportunity_network(selected_opp)
        
        st.markdown("---")
        components.render_evidence_explorer(selected_opp, evidence_list)
    else:
        st.warning("No opportunities to explore. Run discovery first.")

# ==========================================
# Page 6: ▣ Business Models
# ==========================================
elif page == "▣ Business Models":
    st.markdown("## ▣ Business Model Canvas Expansion")
    st.write("Generates the complete 9-block business model canvas for the selected venture:")
    
    opps = st.session_state.opportunities
    if not opps:
        res_active = call_backend("GET", "/opportunities")
        opps = res_active.get("opportunities", [])
        st.session_state.opportunities = opps
        
    if opps:
        opp_names = [o.get("name") for o in opps]
        selected_opp_name = st.selectbox("Select opportunity:", opp_names)
        
        idx = opp_names.index(selected_opp_name)
        selected_opp = opps[idx]
        opp_id = selected_opp.get("id")
        
        if st.button("⚙️ GENERATE BUSINESS MODEL", type="primary"):
            with st.spinner("Expanding canvas blocks via IBM Granite..."):
                res = call_backend("POST", "/expand-business-model", json_data={"opportunity_id": opp_id})
                if res.get("status") != "error":
                    st.session_state.canvas_caches[opp_id] = res
                    st.success("Canvas synthesized successfully!")
                else:
                    st.error(res.get("error"))
                    
        if opp_id in st.session_state.canvas_caches:
            canvas = st.session_state.canvas_caches[opp_id]
            components.render_business_model_canvas(selected_opp, canvas)
        else:
            st.info("Click 'GENERATE BUSINESS MODEL' to call Watsonx expansion.")
    else:
        st.warning("No opportunities to expand. Run discovery first.")

# ==========================================
# Page 7: ◐ Validator
# ==========================================
elif page == "◐ Validator":
    st.markdown("## ◐ Test the Opportunity")
    st.write("Adjust numerical assumptions to test the venture and simulate score changes:")
    
    opps = st.session_state.opportunities
    if not opps:
        res_active = call_backend("GET", "/opportunities")
        opps = res_active.get("opportunities", [])
        st.session_state.opportunities = opps
        
    if opps:
        opp_names = [o.get("name") for o in opps]
        selected_opp_name = st.selectbox("Select opportunity to validate:", opp_names)
        
        idx = opp_names.index(selected_opp_name)
        selected_opp = opps[idx]
        opp_id = selected_opp.get("id")
        
        m = st.slider("Market Potential", 0.0, 100.0, float(selected_opp.get("market_potential", 50.0)))
        f = st.slider("Technical Feasibility", 0.0, 100.0, float(selected_opp.get("feasibility", 50.0)))
        s = st.slider("Strategic Fit Alignment", 0.0, 100.0, float(selected_opp.get("strategic_fit", 50.0)))
        a = st.slider("Asset Reusability", 0.0, 100.0, float(selected_opp.get("asset_reusability", 50.0)))
        c = st.slider("AI Inference Confidence", 0.0, 100.0, float(selected_opp.get("confidence", 50.0)))
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            if st.button("🧪 RUN SIMULATION", type="primary", use_container_width=True):
                with st.spinner("Calculating validated scores..."):
                    payload = {
                        "opportunity_id": opp_id,
                        "market_potential": m,
                        "feasibility": f,
                        "strategic_fit": s,
                        "asset_reusability": a,
                        "confidence": c
                    }
                    res = call_backend("POST", "/validate-opportunity", json_data=payload)
                    if res.get("status") != "error":
                        st.session_state.validation_caches[opp_id] = res
                        st.success("Validation computed successfully.")
                    else:
                        st.error(res.get("error"))
        with col_v2:
            if st.button("RESET ASSUMPTIONS", use_container_width=True):
                if opp_id in st.session_state.validation_caches:
                    del st.session_state.validation_caches[opp_id]
                    st.rerun()
                    
        if opp_id in st.session_state.validation_caches:
            val_data = st.session_state.validation_caches[opp_id]
            components.render_opportunity_validator(selected_opp, val_data)
        else:
            st.info("Adjust the sliders and click 'RUN SIMULATION' to run.")
    else:
        st.warning("No opportunities to validate. Run discovery first.")

# ==========================================
# Page 8: ⇄ Compare
# ==========================================
elif page == "⇄ Compare":
    st.markdown("## ⇄ Compare Discovery Ventures")
    st.write("Select 2 or 3 opportunities to compare metrics:")
    
    opps = st.session_state.opportunities
    if not opps:
        res_active = call_backend("GET", "/opportunities")
        opps = res_active.get("opportunities", [])
        st.session_state.opportunities = opps
        
    if opps:
        selected_opps = []
        for opp in opps:
            box = st.checkbox(opp.get("name"), value=True)
            if box:
                selected_opps.append(opp)
                
        components.render_opportunity_comparison(selected_opps)
    else:
        st.warning("No opportunities loaded. Run discovery first.")

# ==========================================
# Page 9: ◫ Analytics
# ==========================================
elif page == "◫ Analytics":
    st.markdown("## ◫ Venture Analytics Dashboard")
    
    opps = st.session_state.opportunities
    if not opps:
        res_active = call_backend("GET", "/opportunities")
        opps = res_active.get("opportunities", [])
        st.session_state.opportunities = opps
        
    if opps:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### Opportunity Radar Comparison")
            components.render_radar_chart(opps)
        with col2:
            st.markdown("#### Overall Score distribution")
            opp_names = [o.get("name") for o in opps]
            opp_scores = [o.get("overall_score") for o in opps]
            df = pd.DataFrame({"Venture": opp_names, "Overall Score (%)": opp_scores})
            fig = px.bar(
                df, x="Venture", y="Overall Score (%)", 
                color="Overall Score (%)", color_continuous_scale="Purples",
                template="plotly_dark"
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
        st.markdown("#### Feasibility vs Market Potential Correlation Matrix")
        components.render_analytics_page({}, opps)
    else:
        st.warning("Please load or discover opportunities first.")

# ==========================================
# Page 10: ⚙ Architecture
# ==========================================
elif page == "⚙ Architecture":
    st.markdown("## ⚙ Technical System Architecture")
    
    res = call_backend("GET", "/architecture")
    if res.get("status") != "error":
        components.render_architecture_page(res.get("components", []))
    else:
        st.error(res.get("error"))

# ==========================================
# Page 11: ● System
# ==========================================
elif page == "● System":
    st.markdown("## ● Subsystem Health Monitor")
    
    if st.button("🔄 REFRESH STATUS", type="primary"):
        st.rerun()
        
    health = call_backend("GET", "/health")
    if health.get("status") != "error":
        components.render_system_status(health)
    else:
        st.error(health.get("error"))
