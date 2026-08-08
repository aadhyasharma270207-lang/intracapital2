import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def render_header():
    """
    Renders the premium dashboard header and subtitle.
    """
    st.markdown(
        """
        <div style='text-align: center; padding: 1.5rem 0;'>
            <h1 style='font-size: 3.2rem; background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;'>
                INTRACAPITAL
            </h1>
            <p style='font-size: 1.15rem; color: #94a3b8; font-weight: 300; letter-spacing: 0.05em; margin-top: 4px;'>
                Discover Businesses Hidden Inside Businesses.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_home_hero(is_live: bool):
    """
    Renders the 3D-styled Hero section.
    Left: Text metadata and discover triggers.
    Right: Interactive 3D rotating network Canvas drawing orb clusters.
    """
    status_indicator = (
        "<span style='background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); "
        "padding: 4px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);'>🟢 LIVE IBM GRANITE</span>"
        if is_live else
        "<span style='background: rgba(245, 158, 11, 0.12); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); "
        "padding: 4px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);'>🟡 DEMO MODE</span>"
    )
    
    col_left, col_right = st.columns([1.3, 1.0])
    
    with col_left:
        st.markdown(
            f"""
            <div class="hero-container" style="height: 100%; display: flex; flex-direction: column; justify-content: center; margin-bottom: 0;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; color: #38bdf8; font-weight: 700; margin-bottom: 12px; display: block;">AI Venture Discovery Engine</span>
                <h1 class="hero-title" style="margin-top: 0; line-height: 1.15;">INTRACAPITAL</h1>
                <p class="hero-tagline">"Discover Businesses Hidden Inside Businesses."</p>
                <p class="hero-description" style="margin-bottom: 25px; font-size:1rem; color: #cbd5e1;">
                    Turn overlooked company assets, customer signals, research papers, and operational data into your next business opportunity. 
                    INTRACAPITAL acts as a strategic venture-intelligence platform to bridge departments and find the connections you normally overlook.
                </p>
                <div style="margin-top: 10px;">
                    {status_indicator}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_right:
        # Sandboxed iframe Canvas rendering rotating core orbits
        canvas_html = """
        <div style="background: rgba(11, 16, 36, 0.55); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 24px; padding: 15px; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);">
            <canvas id="coreCanvas" width="460" height="380" style="display: block; width: 100%; height: auto;"></canvas>
        </div>
        <script>
            const canvas = document.getElementById('coreCanvas');
            const ctx = canvas.getContext('2d');
            
            const nodes = [
                { name: 'PATENT', x: 0, y: 0, z: 0, angle: 0, radius: 140, speed: 0.012, color: '#38bdf8' },
                { name: 'RESEARCH', x: 0, y: 0, z: 0, angle: 2.09, radius: 140, speed: 0.009, color: '#818cf8' },
                { name: 'CUSTOMER', x: 0, y: 0, z: 0, angle: 4.18, radius: 140, speed: 0.015, color: '#f43f5e' },
                { name: 'SENSOR', x: 0, y: 0, z: 0, angle: 1.04, radius: 110, speed: -0.011, color: '#fb7185' },
                { name: 'OPERATIONS', x: 0, y: 0, z: 0, angle: 3.14, radius: 110, speed: -0.013, color: '#a855f7' },
                { name: 'LOGISTICS', x: 0, y: 0, z: 0, angle: 5.23, radius: 110, speed: -0.010, color: '#c084fc' }
            ];
            
            const centerNode = { name: 'AI CORE', x: 230, y: 190, r: 30, pulse: 0 };
            const opportunities = [];
            
            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw technical grid lines
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.02)';
                ctx.lineWidth = 1;
                for (let i = 0; i < canvas.width; i += 30) {
                    ctx.beginPath();
                    ctx.moveTo(i, 0);
                    ctx.lineTo(i, canvas.height);
                    ctx.stroke();
                }
                for (let j = 0; j < canvas.height; j += 30) {
                    ctx.beginPath();
                    ctx.moveTo(0, j);
                    ctx.lineTo(canvas.width, j);
                    ctx.stroke();
                }
                
                // Pulsing central orb glow
                centerNode.pulse += 0.035;
                const glowSize = centerNode.r + Math.sin(centerNode.pulse) * 5;
                const radGlow = ctx.createRadialGradient(centerNode.x, centerNode.y, 5, centerNode.x, centerNode.y, glowSize * 2.5);
                radGlow.addColorStop(0, 'rgba(56, 189, 248, 0.4)');
                radGlow.addColorStop(0.35, 'rgba(99, 102, 241, 0.2)');
                radGlow.addColorStop(1, 'rgba(5, 8, 22, 0)');
                
                ctx.fillStyle = radGlow;
                ctx.beginPath();
                ctx.arc(centerNode.x, centerNode.y, glowSize * 2.5, 0, Math.PI * 2);
                ctx.fill();
                
                // Inner core boundary
                ctx.fillStyle = 'rgba(11, 16, 36, 0.8)';
                ctx.beginPath();
                ctx.arc(centerNode.x, centerNode.y, centerNode.r, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#38bdf8';
                ctx.lineWidth = 2.5;
                ctx.stroke();
                
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 9px Outfit, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('AI ENGINE', centerNode.x, centerNode.y - 2);
                ctx.fillStyle = '#38bdf8';
                ctx.fillText('CORE', centerNode.x, centerNode.y + 8);
                
                // Draw satellites
                nodes.forEach(node => {
                    node.angle += node.speed;
                    
                    const cosA = Math.cos(node.angle);
                    const sinA = Math.sin(node.angle);
                    
                    node.x = centerNode.x + cosA * node.radius;
                    node.y = centerNode.y + sinA * node.radius * 0.4; // flattened orbit
                    node.z = sinA * 50; 
                    
                    const depthScale = (node.z + 100) / 100;
                    const nodeSize = 10 * depthScale;
                    
                    // Core to satellite line
                    ctx.strokeStyle = `rgba(56, 189, 248, ${0.1 * depthScale})`;
                    ctx.lineWidth = 1 * depthScale;
                    ctx.beginPath();
                    ctx.moveTo(centerNode.x, centerNode.y);
                    ctx.lineTo(node.x, node.y);
                    ctx.stroke();
                    
                    // Outer glow
                    ctx.fillStyle = node.color;
                    ctx.globalAlpha = 0.12 * depthScale;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, nodeSize * 1.6, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Solid inner
                    ctx.globalAlpha = 1.0;
                    ctx.fillStyle = node.color;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, nodeSize * 0.5, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                    
                    // Label
                    ctx.fillStyle = '#94a3b8';
                    ctx.font = `${Math.round(8.5 * depthScale)}px Inter, sans-serif`;
                    ctx.fillText(node.name, node.x, node.y - nodeSize - 5);
                });
                
                // Draw shot-out opportunity particles
                if (Math.random() < 0.015 && opportunities.length < 4) {
                    opportunities.push({
                        x: centerNode.x,
                        y: centerNode.y,
                        vx: (Math.random() - 0.5) * 1.8,
                        vy: -Math.random() * 2.2 - 0.8,
                        alpha: 1.0,
                        size: 6.5,
                        color: '#10b981'
                    });
                }
                
                for (let i = opportunities.length - 1; i >= 0; i--) {
                    const opp = opportunities[i];
                    opp.x += opp.vx;
                    opp.y += opp.vy;
                    opp.alpha -= 0.0075;
                    
                    if (opp.alpha <= 0) {
                        opportunities.splice(i, 1);
                        continue;
                    }
                    
                    ctx.globalAlpha = opp.alpha;
                    ctx.fillStyle = opp.color;
                    ctx.shadowColor = opp.color;
                    ctx.shadowBlur = 8;
                    
                    ctx.beginPath();
                    ctx.arc(opp.x, opp.y, opp.size, 0, Math.PI * 2);
                    ctx.fill();
                    
                    ctx.fillStyle = '#ffffff';
                    ctx.font = '7.5px Inter, sans-serif';
                    ctx.fillText('OPPORTUNITY', opp.x, opp.y - opp.size - 3);
                    
                    ctx.globalAlpha = 1.0;
                    ctx.shadowBlur = 0;
                }
                
                requestAnimationFrame(animate);
            }
            animate();
        </script>
        """
        st.components.v1.html(canvas_html, height=410, scrolling=False)

def render_pipeline_flow(current_step: str):
    """
    Renders an interactive pipeline visual.
    Steps: UPLOAD -> EXTRACT -> CLEAN -> CHUNK -> EMBED -> INDEX -> READY
    """
    steps = ["UPLOAD", "EXTRACT", "CLEAN", "CHUNK", "EMBED", "INDEX", "READY"]
    
    try:
        current_idx = steps.index(current_step.upper())
    except ValueError:
        current_idx = -1
        
    html = '<div class="pipeline-wrapper">'
    for idx, step in enumerate(steps):
        if idx == len(steps) - 1 and current_step.upper() == "READY":
            status_class = "ready active"
        elif idx == current_idx:
            status_class = "active"
        elif idx < current_idx:
            status_class = "completed"
        else:
            status_class = ""
            
        html += f"""
        <div class="pipeline-step {status_class}">
            <span style="font-size: 0.75rem; font-weight: 600; color: { '#cbd5e1' if idx <= current_idx else '#475569' };">{step}</span>
            <div class="pipeline-dot"></div>
        </div>
        """
        if idx < len(steps) - 1:
            html += '<span class="pipeline-arrow">→</span>'
            
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_executive_dashboard(stats: dict, is_live: bool):
    """
    Renders floating metrics card headers.
    """
    engine_label = "🟢 LIVE GRANITE" if is_live else "🟡 DEMO MODE"
    st.markdown(f"### Executive Dashboard Summary — **{engine_label}**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">📁</div>
                <div class="metric-value">{stats.get('documents_processed', 0)}</div>
                <div class="metric-label">Assets Analyzed</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🧩</div>
                <div class="metric-value">{stats.get('chunks', 0)}</div>
                <div class="metric-label">Knowledge Chunks</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🔮</div>
                <div class="metric-value">{stats.get('opportunities', 0)}</div>
                <div class="metric-label">Opps Surfaced</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🧠</div>
                <div class="metric-value">{stats.get('average_confidence', 0.0):.1f}%</div>
                <div class="metric-label">Avg Confidence</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-container" style="border-color: rgba(16, 185, 129, 0.25) !important;">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🏆</div>
                <div class="metric-value" style="background: linear-gradient(135deg, #10b981 0%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{stats.get('top_score', 0.0):.1f}%</div>
                <div class="metric-label">Top Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_opportunity_card(opp: dict, rank: int, is_top: bool = False):
    """
    Renders opportunities inside premium floating cards with SVG score progress rings.
    """
    score = opp.get("overall_score", 0.0)
    container_class = "top-opp-container" if is_top else "opp-card"
    label_html = '<span class="top-opp-label">🏆 Top Discovery Opportunity</span>' if is_top else f'<span class="opp-badge">Venture #{rank}</span>'
    
    # Custom circular progress ring SVG
    progress_svg = f"""
    <svg width="68" height="68" viewBox="0 0 36 36" style="margin-left: 15px; display: block; flex-shrink: 0;">
        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(56, 189, 248, 0.12)" stroke-width="2.8" />
        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="url(#cardGrad)" stroke-width="3" stroke-dasharray="{score}, 100" stroke-linecap="round" />
        <defs>
            <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#c084fc" />
            </linearGradient>
        </defs>
        <text x="18" y="21.5" text-anchor="middle" font-family="Outfit" font-size="8" font-weight="900" fill="#ffffff">{score:.1f}</text>
    </svg>
    """
    
    st.markdown(
        f"""
        <div class="{container_class}">
            {label_html}
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; margin-bottom: 12px;">
                <h2 style="margin: 0; font-size: 1.7rem; color: #ffffff; line-height: 1.25;">{opp.get('name', 'Unnamed Venture')}</h2>
                {progress_svg}
            </div>
            
            <p style="font-size: 1.12rem; font-style: italic; color: #cbd5e1; margin-bottom: 20px; line-height: 1.45; font-weight: 300;">
                "{opp.get('pitch', '')}"
            </p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px;">
                <span class="opp-score-pill">📈 Market Potential: {opp.get('market_potential', 0):.0f}%</span>
                <span class="opp-score-pill">🛠️ Feasibility: {opp.get('feasibility', 0):.0f}%</span>
                <span class="opp-score-pill">🛡️ Strategic Fit: {opp.get('strategic_fit', 0):.0f}%</span>
                <span class="opp-score-pill">♻️ Asset Reuse: {opp.get('asset_reusability', 0):.0f}%</span>
                <span class="opp-score-pill">🧠 Confidence: {opp.get('confidence', 0):.0f}%</span>
            </div>
            
            <div style="font-size: 0.95rem; line-height: 1.5; color: #94a3b8;">
                <strong style="color: #f1f5f9;">Identified Pain Point:</strong>
                <p style="margin-top: 4px; margin-bottom: 12px; color: #cbd5e1;">{opp.get('problem', '')}</p>
                <strong style="color: #f1f5f9;">Proprietary Venture Solution:</strong>
                <p style="margin-top: 4px; margin-bottom: 0; color: #cbd5e1;">{opp.get('solution', '')}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_opportunity_network(opp: dict):
    """
    Renders the 3D-inspired Opportunity Network SVG diagram.
    Highlights only the contributing nodes for the active opportunity.
    """
    assets_used = opp.get("existing_assets", [])
    if isinstance(assets_used, str):
        assets_used = [assets_used]
        
    has_beacon = any("beacon" in str(a).lower() or "10492" in str(a).lower() for a in assets_used)
    has_compressor = any("compressor" in str(a).lower() or "11029" in str(a).lower() for a in assets_used)
    has_logistics = any("logistics" in str(a).lower() or "delay" in str(a).lower() for a in assets_used)
    
    # Define opacity values based on selection
    op_beacon = "1.0" if has_beacon else "0.35"
    op_compressor = "1.0" if has_compressor else "0.35"
    op_logistics = "1.0" if has_logistics else "0.35"
    
    line_beacon_color = "#38bdf8" if has_beacon else "#475569"
    line_compressor_color = "#c084fc" if has_compressor else "#475569"
    line_logistics_color = "#f43f5e" if has_logistics else "#475569"
    
    line_width_beacon = "2.5" if has_beacon else "1"
    line_width_compressor = "2.5" if has_compressor else "1"
    line_width_logistics = "2.5" if has_logistics else "1"
    
    network_svg = f"""
    <div style="background: rgba(11, 16, 36, 0.5); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 20px; padding: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <h4 style="margin-top: 0; color: #fff; text-align: left; font-family: Outfit; font-size:1.15rem; letter-spacing:0.02em;">🛰️ Active Venture Grounding connections</h4>
        <p style="font-size:0.85rem; color:#64748b; text-align:left; margin-bottom:15px; margin-top:-6px;">Highlights the specific technology assets that generated this discovery.</p>
        
        <svg viewBox="0 0 540 280" width="100%" height="auto" style="display: block; margin: 0 auto; max-width: 540px;">
            <!-- Background grids -->
            <line x1="0" y1="70" x2="540" y2="70" stroke="rgba(255,255,255,0.015)" stroke-width="0.8" />
            <line x1="0" y1="140" x2="540" y2="140" stroke="rgba(255,255,255,0.015)" stroke-width="0.8" />
            <line x1="0" y1="210" x2="540" y2="210" stroke="rgba(255,255,255,0.015)" stroke-width="0.8" />
            
            <!-- Connection lines -->
            <!-- Beacon node to Core -->
            <line x1="120" y1="60" x2="270" y2="140" stroke="{line_beacon_color}" stroke-dasharray="{'5,3' if not has_beacon else 'none'}" stroke-width="{line_width_beacon}" opacity="{op_beacon}" />
            
            <!-- Compressor node to Core -->
            <line x1="120" y1="140" x2="270" y2="140" stroke="{line_compressor_color}" stroke-dasharray="{'5,3' if not has_compressor else 'none'}" stroke-width="{line_width_compressor}" opacity="{op_compressor}" />
            
            <!-- Logistics node to Core -->
            <line x1="120" y1="220" x2="270" y2="140" stroke="{line_logistics_color}" stroke-dasharray="{'5,3' if not has_logistics else 'none'}" stroke-width="{line_width_logistics}" opacity="{op_logistics}" />
            
            <!-- Core to Discovery -->
            <line x1="270" y1="140" x2="420" y2="140" stroke="#10b981" stroke-width="3" />
            
            <!-- Central AI Engine Core -->
            <circle cx="270" cy="140" r="32" fill="#0b1024" stroke="#38bdf8" stroke-width="2.5" />
            <circle cx="270" cy="140" r="26" fill="rgba(56, 189, 248, 0.08)" />
            <text x="270" y="143" font-family="Outfit" font-size="7" font-weight="900" fill="#ffffff" text-anchor="middle">AI CORE</text>
            
            <!-- Node A: Beacon Sensor Patent -->
            <g opacity="{op_beacon}">
                <rect x="25" y="40" width="95" height="40" rx="8" fill="#0b1024" stroke="#38bdf8" stroke-width="1.5" />
                <text x="72.5" y="58" font-family="Inter" font-size="7.5" font-weight="700" fill="#ffffff" text-anchor="middle">📡 Mesh Beacon</text>
                <text x="72.5" y="69" font-family="Inter" font-size="6.5" fill="#64748b" text-anchor="middle">PAT-US-104928</text>
            </g>
            
            <!-- Node B: Acoustic Vibration Compressor Patent -->
            <g opacity="{op_compressor}">
                <rect x="25" y="120" width="95" height="40" rx="8" fill="#0b1024" stroke="#c084fc" stroke-width="1.5" />
                <text x="72.5" y="138" font-family="Inter" font-size="7.5" font-weight="700" fill="#ffffff" text-anchor="middle">⚡ Shaft Acoustic</text>
                <text x="72.5" y="149" font-family="Inter" font-size="6.5" fill="#64748b" text-anchor="middle">PAT-US-11029</text>
            </g>
            
            <!-- Node C: Logistics Coordinate delays -->
            <g opacity="{op_logistics}">
                <rect x="25" y="200" width="95" height="40" rx="8" fill="#0b1024" stroke="#f43f5e" stroke-width="1.5" />
                <text x="72.5" y="218" font-family="Inter" font-size="7.5" font-weight="700" fill="#ffffff" text-anchor="middle">🚚 Route Delays</text>
                <text x="72.5" y="229" font-family="Inter" font-size="6.5" fill="#64748b" text-anchor="middle">Operations Logs</text>
            </g>
            
            <!-- Node D: Discovered Opportunity -->
            <g>
                <rect x="420" y="115" width="105" height="50" rx="10" fill="#0b1024" stroke="#10b981" stroke-width="2" />
                <text x="472.5" y="136" font-family="Outfit" font-size="8" font-weight="800" fill="#ffffff" text-anchor="middle">🔮 NEW VENTURE</text>
                <text x="472.5" y="148" font-family="Inter" font-size="6.5" fill="#10b981" text-anchor="middle">{opp.get('name')[:20]}...</text>
            </g>
        </svg>
    </div>
    """
    st.markdown(network_svg, unsafe_allow_html=True)

def render_evidence_explorer(opp: dict, evidence_list: list):
    """
    Renders RAG evidence and connections in the Evidence Explorer.
    """
    st.markdown("### Why this Business Opportunity?")
    
    assets_used = opp.get("existing_assets", [])
    if isinstance(assets_used, str):
        assets_used = [assets_used]
        
    assets_str = " + ".join(assets_used) if assets_used else "Corporate Assets"
    
    st.markdown(
        f"""
        <div class="node-flow">
            <div class="node-box asset">
                📡 <b>EXISTING ASSET A & B:</b><br>{assets_str}
            </div>
            <div class="node-connector">↓</div>
            <div class="node-box problem">
                📉 <b>CUSTOMER PROBLEM / LOGISTICS EXCURSION:</b><br>{opp.get('problem', 'Customer Pain Point')}
            </div>
            <div class="node-connector">↓</div>
            <div class="node-box venture">
                🔮 <b>HIDDEN CONNECTION surfaced:</b><br>{opp.get('asset_connection', 'Connection surfaced')}
            </div>
            <div class="node-connector">↓</div>
            <div class="node-box venture" style="background: rgba(16, 185, 129, 0.15); border-left-color: #10b981;">
                🚀 <b>NEW BUSINESS DISCOVERY:</b><br>{opp.get('name', 'Synthesized Venture')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("#### Retrieved Grounding Evidence Sources")
    relevant_chunks = [
        c for c in evidence_list 
        if any(asset.lower()[:15] in str(c.get("filename", "")).lower() for asset in assets_used)
        or any(asset.lower()[:15] in str(c.get("text", "")).lower() for asset in assets_used)
        or "feedback" in str(c.get("filename", "")).lower() 
        or "sensor" in str(c.get("filename", "")).lower()
    ]
    
    if not relevant_chunks:
        relevant_chunks = evidence_list[:3]
        
    for idx, c in enumerate(relevant_chunks):
        relevance_score = c.get("relevance", 85.0)
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:600;">
                    <span>📜 Source File: <code style="color:#818cf8;">{c.get('filename')}</code> { f'(Page: {c.get("page")})' if c.get('page') else '' }</span>
                    <span style="color:#10b981;">Relevance: {relevance_score}%</span>
                </div>
                <p style="font-size: 0.9rem; color: #94a3b8; font-style: italic; margin-top: 6px; margin-bottom: 0;">
                    "{c.get('text')[:300]}..."
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("#### AI Business Reasoning")
    st.info(opp.get("reasoning", "No detailed reasoning provided."))

def render_radar_chart(opps: list):
    """
    Renders a polar/radar comparison chart.
    """
    if not opps:
        return
        
    categories = ['Market Potential', 'Feasibility', 'Strategic Fit', 'Asset Reusability', 'Confidence']
    fig = go.Figure()
    
    for opp in opps:
        m = opp.get("market_potential", 0)
        f = opp.get("feasibility", 0)
        s = opp.get("strategic_fit", 0)
        a = opp.get("asset_reusability", 0)
        c = opp.get("confidence", 0)
        
        fig.add_trace(go.Scatterpolar(
            r=[m, f, s, a, c, m],
            theta=categories + [categories[0]],
            fill='toself',
            name=opp.get("name")
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#64748b"),
                gridcolor="rgba(255,255,255,0.05)"
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.05)",
                linecolor="rgba(255,255,255,0.1)"
            ),
            bgcolor="rgba(15, 23, 42, 0.45)",
        ),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#f1f5f9"),
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def render_business_model_canvas(opp: dict, canvas: dict):
    """
    Renders the expanded Business Model canvas blocks.
    """
    st.markdown(f"### Business Model Canvas: **{opp.get('name')}**")
    
    col1, col2 = st.columns(2)
    
    def get_labeled_html(field_name, content):
        labels = canvas.get("labels", {})
        label = labels.get(field_name, "Requires validation")
        
        color_map = {
            "Evidence-backed": "#10b981",
            "AI-generated hypothesis": "#38bdf8",
            "Requires validation": "#f43f5e"
        }
        color = color_map.get(label, "#f43f5e")
        
        return f"""
        <div style="background: rgba(11,16,36,0.65); border: 1px solid rgba(56,189,248,0.1); border-left: 4px solid {color}; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
            <div style="display:flex; justify-content:space-between; font-weight:600; font-size:0.85rem; margin-bottom:6px;">
                <span style="color:#fff; text-transform:uppercase; letter-spacing:0.04em; font-family: Outfit;">{field_name.replace('_', ' ')}</span>
                <span style="color:{color}; font-size:0.8rem; font-weight:700;">● {label}</span>
            </div>
            <div style="color:#cbd5e1; font-size:0.95rem; line-height:1.4;">{content}</div>
        </div>
        """

    with col1:
        st.markdown(get_labeled_html("target_customer", canvas.get("target_customer", "")), unsafe_allow_html=True)
        st.markdown(get_labeled_html("value_proposition", canvas.get("value_proposition", "")), unsafe_allow_html=True)
        st.markdown(get_labeled_html("revenue_model", canvas.get("revenue_model", "")), unsafe_allow_html=True)
        st.markdown(get_labeled_html("distribution", canvas.get("distribution", "")), unsafe_allow_html=True)
        st.markdown(get_labeled_html("key_activities", canvas.get("key_activities", "")), unsafe_allow_html=True)
        
    with col2:
        st.markdown(get_labeled_html("key_resources", canvas.get("key_resources", "")), unsafe_allow_html=True)
        st.markdown(get_labeled_html("cost_drivers", canvas.get("cost_drivers", "")), unsafe_allow_html=True)
        st.markdown(get_labeled_html("go_to_market", canvas.get("go_to_market", "")), unsafe_allow_html=True)
        st.markdown(get_labeled_html("first_validation_experiment", canvas.get("first_validation_experiment", "")), unsafe_allow_html=True)

def render_opportunity_validator(opp: dict, val_results: dict):
    """
    Renders the validator score comparison.
    """
    st.markdown(f"### Opportunity Validator: **{opp.get('name')}**")
    
    orig = val_results.get("original_score", opp.get("overall_score", 0.0))
    adj = val_results.get("adjusted_score", orig)
    diff = val_results.get("difference", 0.0)
    
    diff_color = "#10b981" if diff > 0 else "#f43f5e" if diff < 0 else "#64748b"
    diff_sign = "+" if diff > 0 else ""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(
            f"""
            <div style="background: rgba(11,16,36,0.6); border:1px solid rgba(56,189,248,0.1); border-radius:16px; padding:20px; text-align:center; margin-bottom:16px; box-shadow: 0 8px 30px rgba(0,0,0,0.3);">
                <div style="font-size:0.85rem; color:#64748b; text-transform:uppercase; font-weight:600; letter-spacing:0.04em;">Original Calculated Score</div>
                <div style="font-size:3rem; font-weight:800; color:#38bdf8; margin: 6px 0; font-family: Outfit;">{orig:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div style="background: rgba(11,16,36,0.6); border:1px solid rgba(56,189,248,0.1); border-radius:16px; padding:20px; text-align:center; margin-bottom:16px; box-shadow: 0 8px 30px rgba(0,0,0,0.3);">
                <div style="font-size:0.85rem; color:#64748b; text-transform:uppercase; font-weight:600; letter-spacing:0.04em;">Adjusted Validation Score</div>
                <div style="font-size:3rem; font-weight:800; color:#10b981; margin: 6px 0; font-family: Outfit;">{adj:.1f}%</div>
                <div style="color:{diff_color}; font-weight:700; font-size:1.05rem;">Difference: {diff_sign}{diff:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("**Slider calculations weights breakdown explanation:**")
    st.code(val_results.get("score_explanation", opp.get("score_explanation", "")))

def render_opportunity_comparison(opps: list):
    """
    Renders comparative tables for selected opportunities.
    """
    if not opps:
        st.warning("Select opportunities in the compare view to compile comparative metrics.")
        return
        
    rows = []
    for opp in opps:
        rows.append({
            "Opportunity Name": opp.get("name"),
            "Overall Match Score": f"{opp.get('overall_score', 0.0):.1f}%",
            "Market Potential": f"{opp.get('market_potential', 0.0):.0f}/100",
            "Feasibility": f"{opp.get('feasibility', 0.0):.0f}/100",
            "Strategic Fit": f"{opp.get('strategic_fit', 0.0):.0f}/100",
            "Asset Reusability": f"{opp.get('asset_reusability', 0.0):.0f}/100",
            "Confidence": f"{opp.get('confidence', 0.0):.0f}/100",
            "Revenue Model": opp.get("revenue_model", "N/A")
        })
        
    df = pd.DataFrame(rows)
    st.table(df)
    
    st.success(f"💡 **Recommended Strongest Venture:** `{opps[0].get('name')}` has the highest corporate asset feasibility match of **{opps[0].get('overall_score')}%**.")

def render_analytics_page(stats: dict, opps: list):
    """
    Visualizes document structures, score spreads, and categories.
    """
    st.markdown("### Corporate Venture Portfolio Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Document files by type pie chart
        file_counts = {"PDF": 1, "TXT": 4, "CSV": 1} 
        df_docs = pd.DataFrame(list(file_counts.items()), columns=["Type", "Count"])
        fig_pie = px.pie(
            df_docs,
            values="Count",
            names="Type",
            title="Ingested Corporate Documents by Extension Type",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        # 2. Opportunity Match Scores distribution
        opp_names = [o.get("name") for o in opps]
        opp_scores = [o.get("overall_score") for o in opps]
        df_scores = pd.DataFrame({"Opportunity": opp_names, "Overall Score": opp_scores})
        fig_bar = px.bar(
            df_scores,
            x="Opportunity",
            y="Overall Score",
            title="Overall Score distribution across Opportunities",
            color="Overall Score",
            color_continuous_scale="Purples",
            template="plotly_dark"
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("### Market Potential vs Feasibility Correlation Matrix")
    df_scatter = pd.DataFrame({
        "Opportunity": [o.get("name") for o in opps],
        "Market Potential": [o.get("market_potential") for o in opps],
        "Feasibility": [o.get("feasibility") for o in opps],
        "Confidence": [o.get("confidence") for o in opps]
    })
    fig_scatter = px.scatter(
        df_scatter,
        x="Feasibility",
        y="Market Potential",
        size="Confidence",
        color="Opportunity",
        hover_name="Opportunity",
        title="Venture Feasibility vs Market Potential (Bubble size = AI Confidence)",
        template="plotly_dark"
    )
    fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_scatter, use_container_width=True)

def render_architecture_page(components: list):
    """
    Renders details of the system components.
    """
    st.markdown("### Interactive System Architecture Flowchart")
    
    st.markdown(
        """
        ```mermaid
        graph TD
            A[Company Data: PDF, TXT, CSV] -->|Ingestion & Filtering| B[FastAPI Backend: api.py]
            B -->|Text Chunking| C[Embeddings: sentence-transformers]
            C -->|Persistent vectors| D[ChromaDB Vector database]
            D -->|RAG retrieval| E[RAG context builder]
            E -->|Synthesized queries| F[IBM Granite API watsonx.ai]
            F -->|JSON schema payload| G[Opportunity Discovery Engine]
            G -->|Scoring weights calculation| H[Transparent Scoring Python]
            H -->|REST Client API calls| I[Streamlit Frontend Dashboard]
            
            style A fill:#1e293b,stroke:#475569,stroke-width:2px;
            style F fill:#4f46e5,stroke:#818cf8,stroke-width:2px,color:#fff;
            style I fill:#0f766e,stroke:#0d9488,stroke-width:2px,color:#fff;
        ```
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("#### Components Glossary (Hover/Expand for details)")
    for comp in components:
        with st.expander(f"⚙️ {comp.get('id')}"):
            st.write(comp.get("desc"))

def render_system_status(status: dict):
    """
    Renders subsystem health parameters in a table with badges.
    """
    st.markdown("### Environment Subsystem Monitor")
    
    for key, val in status.items():
        badge_color = "#10b981" if val == "online" else "#f43f5e"
        badge_text = "ONLINE" if val == "online" else "OFFLINE"
        
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; background: rgba(11,16,36,0.65); border:1px solid rgba(56,189,248,0.12); border-radius:12px; padding:16px; margin-bottom:10px; align-items:center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <span style="font-weight:600; font-size:0.95rem; text-transform:uppercase; color:#cbd5e1; font-family: Outfit;">{key} STATUS</span>
                <span style="background-color:{badge_color}; color:#fff; font-weight:bold; font-size:0.75rem; padding:4px 12px; border-radius:6px; box-shadow: 0 0 12px {badge_color}60;">{badge_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
