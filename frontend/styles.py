import streamlit as st

# Custom CSS for INTRACAPITAL Enterprise AI Design
CUSTOM_CSS = """
<style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Body and Font Settings */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.07) 0%, rgba(5, 8, 22, 0) 50%),
                    radial-gradient(circle at 10% 80%, rgba(168, 85, 247, 0.07) 0%, rgba(5, 8, 22, 0) 50%),
                    #050816 !important;
        color: #f1f5f9 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #ffffff;
    }

    /* 3D Sidebar navigation overrides */
    [data-testid="stSidebar"] {
        background-color: #0b1024 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
        box-shadow: 5px 0 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Premium style navigation buttons */
    div[data-testid="stSidebarUserContent"] .stRadio > div {
        gap: 6px !important;
    }
    
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background: rgba(15, 23, 42, 0.35) !important;
        border: 1px solid rgba(255,255,255,0.02) !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        margin-bottom: 4px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02) !important;
    }
    
    div[data-testid="stSidebarUserContent"] .stRadio label:hover {
        background: rgba(56, 189, 248, 0.08) !important;
        border-color: rgba(56, 189, 248, 0.25) !important;
        color: #ffffff !important;
        transform: translateX(4px) !important;
    }
    
    div[data-testid="stSidebarUserContent"] .stRadio label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(192, 132, 252, 0.15) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Landing Hero Section */
    .hero-container {
        text-align: left;
        padding: 3rem 2.5rem;
        background: rgba(11, 16, 36, 0.5) !important;
        border-radius: 24px;
        margin-bottom: 2rem;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.04);
        position: relative;
        overflow: hidden;
    }
    
    .hero-title {
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em !important;
    }
    
    .hero-tagline {
        font-size: 1.4rem !important;
        color: #cbd5e1 !important;
        font-weight: 400 !important;
        margin-bottom: 1rem !important;
        letter-spacing: 0.02em;
        line-height: 1.3;
    }
    
    .hero-description {
        color: #94a3b8;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }

    /* Executive Metric Card with 3D Depth Hover */
    .metric-container {
        background: rgba(11, 16, 36, 0.6) !important;
        border: 1px solid rgba(56, 189, 248, 0.1) !important;
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.02);
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        perspective: 1000px;
        transform-style: preserve-3d;
    }
    
    .metric-container:hover {
        transform: perspective(1000px) rotateX(3deg) rotateY(-2deg) translateY(-6px);
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 16px 40px rgba(56, 189, 248, 0.12), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        text-shadow: 0 4px 15px rgba(56, 189, 248, 0.1);
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }

    /* Enterprise Standard Opportunity Card - 3D Tilt Effect */
    .opp-card {
        background: rgba(11, 16, 36, 0.55) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(56, 189, 248, 0.12) !important;
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 26px;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.02);
        perspective: 1200px;
        transform-style: preserve-3d;
    }
    
    .opp-card:hover {
        transform: perspective(1200px) rotateX(2deg) rotateY(3deg) translateY(-8px) scale(1.005);
        border-color: rgba(56, 189, 248, 0.45) !important;
        box-shadow: 0 20px 50px rgba(56, 189, 248, 0.16), inset 0 1px 0 rgba(255,255,255,0.06);
    }
    
    .opp-badge {
        font-size: 0.7rem;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0.12em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        display: inline-block;
    }
    
    .opp-score-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        background-color: rgba(56, 189, 248, 0.08);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }

    /* Prominent Top Opportunity Card with Indigo Aura */
    .top-opp-container {
        background: linear-gradient(145deg, rgba(56, 189, 248, 0.08) 0%, rgba(99, 102, 241, 0.05) 100%) !important;
        border: 2px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 25px 60px rgba(56, 189, 248, 0.15), inset 0 1px 0 rgba(255,255,255,0.04) !important;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        perspective: 1200px;
        transform-style: preserve-3d;
    }
    
    .top-opp-container:hover {
        transform: perspective(1200px) rotateX(-2deg) rotateY(3deg) translateY(-8px) scale(1.005);
        border-color: rgba(56, 189, 248, 0.6) !important;
        box-shadow: 0 35px 70px rgba(56, 189, 248, 0.22), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    }
    
    .top-opp-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 900;
        letter-spacing: 0.15em;
        color: #f43f5e;
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 2px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 12px;
        background: rgba(244, 63, 94, 0.08);
    }

    /* 3D Visual Chain Nodes */
    .node-flow {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin: 20px 0;
        padding: 24px;
        background: rgba(11, 16, 36, 0.4) !important;
        border-radius: 16px;
        border: 1px solid rgba(56, 189, 248, 0.08) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .node-box {
        padding: 14px 20px;
        border-radius: 10px;
        font-size: 0.95rem;
        border-left: 4px solid #38bdf8;
        background: rgba(15, 23, 42, 0.4);
        color: #cbd5e1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.25s ease;
    }
    
    .node-box:hover {
        transform: translateX(6px);
        background: rgba(15, 23, 42, 0.6);
    }
    
    .node-box.asset {
        border-left-color: #38bdf8;
    }
    
    .node-box.problem {
        border-left-color: #f43f5e;
    }
    
    .node-box.venture {
        border-left-color: #10b981;
        font-weight: 600;
    }
    
    .node-connector {
        text-align: center;
        font-size: 1.2rem;
        font-weight: 800;
        color: rgba(56, 189, 248, 0.3);
        margin: 2px 0;
    }

    /* Data Pipeline Indicators */
    .pipeline-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(11, 16, 36, 0.5) !important;
        border: 1px solid rgba(56, 189, 248, 0.12) !important;
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 24px;
        overflow-x: auto;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.4);
    }
    
    .pipeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        opacity: 0.35;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .pipeline-step.active {
        opacity: 1.0;
        transform: scale(1.08);
    }
    
    .pipeline-step.completed {
        opacity: 0.8;
    }
    
    .pipeline-dot {
        width: 14px;
        height: 14px;
        border-radius: 9999px;
        background-color: #475569;
        border: 2px solid #050816;
        transition: all 0.3s ease;
    }
    
    .pipeline-step.active .pipeline-dot {
        background-color: #38bdf8;
        box-shadow: 0 0 14px #38bdf8;
    }
    
    .pipeline-step.completed .pipeline-dot {
        background-color: #10b981;
    }
    
    .pipeline-step.ready .pipeline-dot {
        background-color: #10b981;
        box-shadow: 0 0 14px #10b981;
    }

    /* 3D File Upload Area Drop Zone */
    .stFileUploader {
        background: rgba(11, 16, 36, 0.45);
        border: 2px dashed rgba(56, 189, 248, 0.25) !important;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .stFileUploader:hover {
        border-color: rgba(56, 189, 248, 0.6) !important;
        background: rgba(11, 16, 36, 0.6);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.08), inset 0 2px 10px rgba(0,0,0,0.3);
    }

    /* Custom Streamlit expanders override */
    .streamlit-expanderHeader {
        background-color: rgba(11, 16, 36, 0.4) !important;
        border: 1px solid rgba(56, 189, 248, 0.1) !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        margin-bottom: 6px;
        transition: all 0.3s ease;
    }
    .streamlit-expanderHeader:hover {
        background-color: rgba(11, 16, 36, 0.6) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
    }
    .streamlit-expanderContent {
        background-color: rgba(11, 16, 36, 0.2) !important;
        border: 1px solid rgba(56, 189, 248, 0.05) !important;
        border-top: none !important;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        padding: 16px !important;
    }

    /* Custom scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(5, 8, 22, 0.8);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(56, 189, 248, 0.15);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(56, 189, 248, 0.3);
    }
</style>
"""

def inject_premium_styles():
    """
    Injects global premium design system tokens and custom CSS classes.
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
