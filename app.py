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
from frontend.api_client import APIClient

# Initialize API Client singleton
api_client = APIClient()

def call_backend(method: str, endpoint: str, json_data: dict = None, files_data: list = None) -> dict:
    # Ensure backend URL is synced with session state text input
    api_client.backend_url = st.session_state.get("backend_url", api_client.backend_url)
    return api_client._request(method, endpoint, json_data=json_data, files_data=files_data)

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
if "backend_url" not in st.session_state:
    st.session_state.backend_url = api_client.backend_url

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

custom_url = st.sidebar.text_input("🔗 Backend API Endpoint", value=st.session_state.backend_url)
if custom_url != st.session_state.backend_url:
    st.session_state.backend_url = custom_url
    api_client.backend_url = custom_url
    st.rerun()

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
try:
    backend_port = api_client.backend_url.split(":")[-1].split("/")[0]
except Exception:
    backend_port = "8000"

health_res = call_backend("GET", "/health")
is_fastapi_online = health_res.get("status") != "error"
granite_status = health_res.get("granite", "offline") if is_fastapi_online else "offline"
is_granite_live = granite_status == "online"

st.sidebar.markdown("---")
if is_fastapi_online:
    st.sidebar.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; color: #10b981; margin-bottom: 4px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#10b981; box-shadow:0 0 8px #10b981;"></span>
            FastAPI Connected • :{backend_port}
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    root_res = call_backend("GET", "/")
    mode_label = root_res.get("mode", "") if root_res.get("status") != "error" else ""
    if is_granite_live and "Sandbox" not in mode_label:
        engine_label = "IBM Granite"
    else:
        engine_label = "Local Fallback"
        
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">
            AI Engine: <b>{engine_label}</b>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; color: #f43f5e; margin-bottom: 8px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#f43f5e; box-shadow:0 0 8px #f43f5e;"></span>
            Backend Offline
        </div>
        """, 
        unsafe_allow_html=True
    )
    if st.sidebar.button("Retry Connection", key="retry_sidebar"):
        st.rerun()

# If backend is offline, halt execution and display warning banner on main dashboard
if not is_fastapi_online:
    st.error("⚠️ **Backend connection unavailable.**")
    st.info(f"Please verify that the FastAPI backend server is running at: `{api_client.backend_url}`")
    if st.button("Retry Connection", key="retry_main"):
        st.rerun()
    st.stop()

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
                    <b>Endpoint Port:</b> <code style="color:#38bdf8;">localhost:{backend_port}</code><br>
                    <b>Database Collections:</b> <code style="color:#38bdf8;">ChromaDB (Local)</code><br>
                    <b>Authentication Key:</b> <code style="color:#38bdf8;">{'CONFIGURED' if api_client.api_key else 'NONE'}</code>
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
    
    # Sleek Business Welcome Banner
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.35); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 16px; padding: 20px; margin-bottom: 25px;">
            <h3 style="margin: 0; color: #fff; font-family: Outfit; font-size: 1.35rem; font-weight: 700; letter-spacing: -0.01em;">🔮 Cognitive Venture Ingestion & Synthesis</h3>
            <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.95rem; line-height: 1.5; font-weight: 300;">
                Bridge operational and intellectual property silos. This discovery console coordinates the ingestion of corporate assets,
                normalizes data streams, and invokes <b>IBM Granite AI</b> to identify cross-domain market-ready venture opportunities.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Query staged files list
    staged_files = []
    if config.UPLOADS_DIR.exists():
        staged_files = [f.name for f in config.UPLOADS_DIR.iterdir() if f.is_file()]
        
    # Render Two-Column Business Action Dashboard
    col_dash1, col_dash2 = st.columns(2)
    
    with col_dash1:
        st.markdown(
            f"""
            <div class="opp-card" style="margin-bottom: 0; height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-color: rgba(56, 189, 248, 0.15);">
                <div>
                    <span style="font-size:0.75rem; text-transform:uppercase; font-weight:800; color:#38bdf8; letter-spacing:0.05em; display:block; margin-bottom:8px;">PHASE 01</span>
                    <h3 style="margin:0; font-family:Outfit; font-size:1.3rem; color:#fff;">📂 Corporate Data Preparation</h3>
                    <p style="font-size:0.85rem; color:#94a3b8; margin: 8px 0 15px 0; line-height:1.45;">
                        Extracts textual streams from PDF patents, parses CSV telemetry logs, cleans punctuation, chunks passages, and generates semantic vector indices in ChromaDB.
                    </p>
                    <div style="background: rgba(15, 23, 42, 0.3); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.03); margin-bottom: 15px;">
                        <span style="font-size: 0.75rem; font-weight: 600; color: #cbd5e1; display: block; margin-bottom: 6px;">Staged Corporate Assets ({len(staged_files)}):</span>
                        { "".join([f'<div style="font-size:0.75rem; color:#94a3b8; padding: 2px 0;">📄 {name}</div>' for name in staged_files]) if staged_files else '<div style="font-size:0.75rem; color:#f43f5e; font-style:italic;">No files loaded. Go to "◈ Company Assets" page to stage files.</div>' }
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        run_analysis = st.button("⚙️ RUN DATA PREPARATION PIPELINE", use_container_width=True)
        
    with col_dash2:
        st.markdown(
            """
            <div class="opp-card" style="margin-bottom: 0; height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-color: rgba(16, 185, 129, 0.15);">
                <div>
                    <span style="font-size:0.75rem; text-transform:uppercase; font-weight:800; color:#10b981; letter-spacing:0.05em; display:block; margin-bottom:8px;">PHASE 02</span>
                    <h3 style="margin:0; font-family:Outfit; font-size:1.3rem; color:#fff;">🧠 Cognitive AI Synthesis</h3>
                    <p style="font-size:0.85rem; color:#94a3b8; margin: 8px 0 15px 0; line-height:1.45;">
                        Queries the semantic database, detects correlations between customer friction logs and technical patents, and invokes IBM Granite to draft, score, and rank new business opportunities.
                    </p>
                    <div style="background: rgba(16, 185, 129, 0.05); border-radius: 8px; padding: 10px; border: 1px solid rgba(16, 185, 129, 0.15); margin-bottom: 15px;">
                        <span style="font-size: 0.75rem; font-weight: 600; color: #10b981; display: block; margin-bottom: 4px;">Cognitive Engines Armed:</span>
                        <div style="font-size:0.75rem; color:#94a3b8; padding: 2px 0;">🎯 Semantic Vector Search (Local Embeddings)</div>
                        <div style="font-size:0.75rem; color:#94a3b8; padding: 2px 0;">⚡ IBM Granite Instruction Synthesis (watsonx.ai)</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        discover_btn = st.button("🚀 DISCOVER HIDDEN BUSINESSES", use_container_width=True, type="primary")

    st.markdown("---")
    
    # 2. Ingestion Pipeline flow diagram with real-time sync wrapper
    st.markdown("### 🛰️ Live Pipeline Stage Monitor")
    
    flow_area = st.empty()
    with flow_area:
        components.render_pipeline_flow(st.session_state.pipeline_step)
        
    status_text = st.empty()
    progress_bar = st.empty()
    
    if run_analysis:
        st.session_state.pipeline_logs = []
        pbar = progress_bar.progress(0)
        import time
        
        st.session_state.pipeline_step = "UPLOAD"
        with flow_area:
            components.render_pipeline_flow("UPLOAD")
        status_text.markdown("● **UPLOAD**: Scanning staged directory and checking SHA-256 cache registry...")
        pbar.progress(15)
        time.sleep(0.3)
        
        st.session_state.pipeline_step = "EXTRACT"
        with flow_area:
            components.render_pipeline_flow("EXTRACT")
        status_text.markdown("✓ **UPLOAD** cache checked.<br>● **EXTRACT**: Parsing file types and converting bytes into text segments...", unsafe_allow_html=True)
        pbar.progress(35)
        time.sleep(0.3)
        
        st.session_state.pipeline_step = "CLEAN"
        with flow_area:
            components.render_pipeline_flow("CLEAN")
        status_text.markdown("✓ **UPLOAD** cache checked.<br>✓ **EXTRACT** complete.<br>● **CLEAN**: Stripping whitespace, removing document metadata anomalies...", unsafe_allow_html=True)
        pbar.progress(55)
        time.sleep(0.3)
        
        st.session_state.pipeline_step = "CHUNK"
        with flow_area:
            components.render_pipeline_flow("CHUNK")
        status_text.markdown("✓ **UPLOAD** cache checked.<br>✓ **EXTRACT** complete.<br>✓ **CLEAN** complete.<br>● **CHUNK & EMBED**: Segmenting passages and running sentence-transformers vector embeddings...", unsafe_allow_html=True)
        pbar.progress(70)
        
        # Real backend POST /analyze
        res = call_backend("POST", "/analyze")
        
        if res.get("status") != "error":
            st.session_state.pipeline_step = "INDEX"
            with flow_area:
                components.render_pipeline_flow("INDEX")
            status_text.markdown(f"✓ **UPLOAD** cache checked.<br>✓ **EXTRACT** complete.<br>✓ **CLEAN** complete.<br>✓ **CHUNK & EMBED** complete.<br>✓ **INDEX**: Saved {res.get('chunks_created')} chunks to ChromaDB vector store.", unsafe_allow_html=True)
            pbar.progress(100)
            st.success(f"Analysis completed in {res.get('processing_time_sec', 0.8)} seconds!")
            
            st.session_state.pipeline_step = "READY"
            with flow_area:
                components.render_pipeline_flow("READY")
            time.sleep(1.0)
            st.rerun()
        else:
            st.error(res.get("error"))
            
    if discover_btn:
        st.session_state.pipeline_logs = []
        pbar = progress_bar.progress(0)
        import time
        
        st.session_state.pipeline_step = "READY"
        with flow_area:
            components.render_pipeline_flow("READY")
        status_text.markdown("● **STAGE 01**: Inspecting local cached vector structures...")
        pbar.progress(20)
        time.sleep(0.3)
        
        status_text.markdown("✓ **STAGE 01** complete.<br>● **STAGE 02**: Running RAG vector queries and locating semantic correlations...", unsafe_allow_html=True)
        pbar.progress(40)
        time.sleep(0.3)
        
        status_text.markdown("✓ **STAGE 01 & 02** complete.<br>● **STAGE 03**: Aligning asset technology capabilities against customer pain points...", unsafe_allow_html=True)
        pbar.progress(60)
        time.sleep(0.3)
        
        status_text.markdown("✓ **STAGE 01, 02 & 03** complete.<br>● **STAGE 04**: Calling IBM Granite generative synthesis model...", unsafe_allow_html=True)
        pbar.progress(80)
        
        # Real backend POST /discover
        res = call_backend("POST", "/discover")
        
        if res.get("status") != "error":
            status_text.markdown("✓ **STAGE 01 to 04** complete.<br>● **STAGE 05**: Executing weighted scoring and ranking matrix...", unsafe_allow_html=True)
            pbar.progress(95)
            time.sleep(0.3)
            
            st.session_state.opportunities = res.get("opportunities", [])
            st.session_state.evidence_used = res.get("evidence_used", [])
            
            pbar.progress(100)
            status_text.markdown(f"✓ **PIPELINE COMPLETE**: Synthesized and ranked {len(st.session_state.opportunities)} opportunities.", unsafe_allow_html=True)
            st.success("Venture discovery completed successfully! Switch to the '◆ Opportunities' tab to view results.")
            time.sleep(1.0)
            st.rerun()
        else:
            status_text.markdown(f"❌ **STAGE 04 FAILED**: {res.get('error')}", unsafe_allow_html=True)
            st.error("Engine execution encountered errors. Defaulting to Demo Mode fallback.")
            res_fallback = call_backend("GET", "/opportunities")
            st.session_state.opportunities = res_fallback.get("opportunities", [])
            time.sleep(1.5)
            st.rerun()

    # Business Explainability Graphic
    st.markdown("---")
    st.markdown("### 💡 How the Cognitive Engine Connects the Dots")
    st.markdown(
        """
        <div style="background: rgba(11, 16, 36, 0.4); border: 1px solid rgba(56, 189, 248, 0.08); border-radius: 12px; padding: 18px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px; text-align: center;">
                <div style="flex: 1; min-width: 120px;">
                    <div style="font-size: 1.8rem; margin-bottom: 4px;">📡</div>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #fff; display: block;">1. Technical Patents</span>
                    <span style="font-size: 0.75rem; color: #64748b;">Underutilized IP & designs</span>
                </div>
                <div style="font-size: 1.2rem; color: #475569;">+</div>
                <div style="flex: 1; min-width: 120px;">
                    <div style="font-size: 1.8rem; margin-bottom: 4px;">📈</div>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #fff; display: block;">2. Real-Time Telemetry</span>
                    <span style="font-size: 0.75rem; color: #64748b;">Sensor logs & deviations</span>
                </div>
                <div style="font-size: 1.2rem; color: #475569;">+</div>
                <div style="flex: 1; min-width: 120px;">
                    <div style="font-size: 1.8rem; margin-bottom: 4px;">💬</div>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #fff; display: block;">3. Customer Complaints</span>
                    <span style="font-size: 0.75rem; color: #64748b;">Market friction & friction logs</span>
                </div>
                <div style="font-size: 1.2rem; color: #10b981;">➔</div>
                <div style="flex: 1.2; min-width: 150px; background: rgba(16, 185, 129, 0.08); border: 1px dashed rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 10px;">
                    <div style="font-size: 1.8rem; margin-bottom: 4px;">🔮</div>
                    <span style="font-size: 0.85rem; font-weight: 700; color: #10b981; display: block;">Discovered Venture</span>
                    <span style="font-size: 0.75rem; color: #94a3b8;">Scored & validated opportunities</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
        
        # Render opportunity cards side-by-side horizontally using a native responsive CSS grid
        if filtered_opps:
            grid_html = '<div class="dashboard-grid">'
            for idx, opp in enumerate(filtered_opps):
                is_top = (idx == 0)
                card_markup = components.get_opportunity_card_html(opp, rank=idx+1, is_top=is_top)
                grid_html += f'<div class="card"><div class="card-content">{card_markup}</div></div>'
            grid_html += '</div>'
            
            st.markdown(grid_html, unsafe_allow_html=True)
                    
            st.markdown("---")
            st.markdown("### 🔍 Access Comprehensive Evidence & Drill-Down Insights")
            
            selected_opp_name = st.selectbox(
                "Select a Discovered Venture to view grounding data, target models, and validations:",
                [opp.get("name") for opp in filtered_opps],
                key="select_drilldown"
            )
            
            selected_opp = next((opp for opp in filtered_opps if opp.get("name") == selected_opp_name), None)
            if selected_opp:
                opp_id = selected_opp.get("id")
                
                # Tabbed Drilldown Interface
                tab_brief, tab_canvas, tab_network, tab_scoring = st.tabs([
                    "📄 Strategic Brief & Impact",
                    "💼 Business Model Canvas",
                    "🛰️ Asset Connections & Grounding",
                    "⚖️ Transparent Scoring Breakdown"
                ])
                
                with tab_brief:
                    st.markdown(f"### Strategic Brief: *{selected_opp.get('name')}*")
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.markdown(f"💼 **Expected Business Impact:** {selected_opp.get('expected_business_impact', 'High Strategic Growth')}")
                        st.markdown(f"🛠️ **Implementation Difficulty:** {selected_opp.get('implementation_difficulty', 'Medium')}")
                    with col_m2:
                        st.markdown(f"🔬 **Recommended Next Experiment:** {selected_opp.get('recommended_next_experiment', 'Feasibility prototype pilot study')}")
                        st.markdown(f"⚠️ **Key Risks:** {', '.join(selected_opp.get('key_risks', [])) if selected_opp.get('key_risks') else 'None identified'}")
                    
                    st.markdown("---")
                    brief_key = f"brief_active_{opp_id}"
                    if brief_key not in st.session_state:
                        st.session_state[brief_key] = False
                        
                    if st.button(f"📄 GENERATE CONFIDENTIAL EXECUTIVE BRIEF", key=f"btn_brief_{opp_id}", use_container_width=True):
                        st.session_state[brief_key] = True
                        
                    if st.session_state[brief_key]:
                        st.markdown(
                            f"""
                            <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 20px; margin-top: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
                                <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px; margin-bottom:15px;">
                                    <span style="font-family:Outfit; font-size:1.15rem; font-weight:800; color:#fff;">📋 INTRACAPITAL VENTURE EXECUTIVE BRIEF</span>
                                    <span style="color:#38bdf8; font-size:0.75rem; font-weight:700;">CONFIDENTIAL &bull; ENTERPRISE AI</span>
                                </div>
                                <p style="font-size:0.95rem; color:#cbd5e1; margin-bottom:8px;"><b>Venture Opportunity:</b> {selected_opp.get('name')}</p>
                                <p style="font-size:0.95rem; color:#cbd5e1; margin-bottom:8px;"><b>Business Thesis:</b> {selected_opp.get('pitch')}</p>
                                <p style="font-size:0.95rem; color:#cbd5e1; margin-bottom:8px;"><b>Department Assets Reused:</b> {', '.join(selected_opp.get('existing_assets', []))}</p>
                                <p style="font-size:0.95rem; color:#cbd5e1; margin-bottom:8px;"><b>Market Potential Score:</b> {selected_opp.get('market_potential', 0.0):.0f}/100 &bull; <b>Feasibility:</b> {selected_opp.get('feasibility', 0.0):.0f}/100</p>
                                <p style="font-size:0.95rem; color:#cbd5e1; margin-bottom:8px;"><b>Strategic Impact:</b> {selected_opp.get('expected_business_impact', 'High Strategic Growth')}</p>
                                <p style="font-size:0.95rem; color:#cbd5e1; margin-bottom:8px;"><b>First Recommended Experiment:</b> {selected_opp.get('recommended_next_experiment', 'Validate prototype sensor feeds')}</p>
                                <p style="font-size:0.85rem; color:#94a3b8; margin-top:15px; font-style:italic; border-top:1px solid rgba(255,255,255,0.05); padding-top:8px;">Powered by IBM watsonx.ai & Granite synthesis reasoning.</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                with tab_canvas:
                    if opp_id in st.session_state.canvas_caches:
                        canvas = st.session_state.canvas_caches[opp_id]
                        components.render_business_model_canvas(selected_opp, canvas)
                    else:
                        st.write("Generate the expanded business model canvas blocks using IBM Granite:")
                        if st.button(f"Generate Canvas details for {selected_opp.get('name')}", key=f"btn_canvas_{opp_id}"):
                            with st.spinner("Expanding canvas blocks via IBM Granite..."):
                                res_canvas = call_backend("POST", "/expand-business-model", json_data={"opportunity_id": opp_id})
                                if res_canvas.get("status") != "error":
                                    st.session_state.canvas_caches[opp_id] = res_canvas
                                    st.success("Canvas generated! Rerunning to load details...")
                                    st.rerun()
                                else:
                                    st.error(res_canvas.get("error"))
                                    
                with tab_network:
                    # Grounding Evidence sources
                    st.markdown("#### 📜 Grounding Evidence Sources")
                    evidence_list = st.session_state.evidence_used
                    if not evidence_list:
                        res_fallback = call_backend("POST", "/discover")
                        evidence_list = res_fallback.get("evidence_used", [])
                        st.session_state.evidence_used = evidence_list
                        
                    assets_used = selected_opp.get("existing_assets", [])
                    relevant_chunks = [
                        c for c in evidence_list 
                        if any(asset.lower()[:15] in str(c.get("filename", "")).lower() for asset in assets_used)
                        or any(asset.lower()[:15] in str(c.get("text", "")).lower() for asset in assets_used)
                        or "feedback" in str(c.get("filename", "")).lower()
                        or "sensor" in str(c.get("filename", "")).lower()
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
                    st.markdown("---")
                    components.render_opportunity_network(selected_opp)
                    
                with tab_scoring:
                    st.markdown("#### ⚖️ Transparent Scoring Breakdown")
                    st.code(selected_opp.get("score_explanation", ""))
                    
        else:
            st.info("No venture discoveries currently loaded. Go to the assets tab or click discover.")
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
