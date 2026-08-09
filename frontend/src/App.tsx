import React, { useState, useEffect, useRef } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Radar, RadarChart, PolarGrid, PolarAngleAxis
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building2, FileText, Activity, Compass, Brain, Layers, 
  Sliders, ShieldCheck, CheckSquare, BarChart3, HelpCircle, 
  Upload, Trash2, ArrowRight, RefreshCw, AlertTriangle, 
  CheckCircle2, ChevronLeft, ChevronRight, Eye
} from 'lucide-react';

import { companyApi } from './api/companyApi';
import type { Company } from './api/companyApi';
import { assetApi } from './api/assetApi';
import type { Asset } from './api/assetApi';
import { processingApi } from './api/processingApi';
import type { ProcessingJob } from './api/processingApi';
import { discoveryApi } from './api/discoveryApi';
import { opportunityApi } from './api/opportunityApi';
import type { Opportunity, OpportunityDetail, CompareResponse } from './api/opportunityApi';
import type { OpportunityEvidenceResponse } from './api/evidenceApi';
import { validationApi } from './api/validationApi';
import { analyticsApi } from './api/analyticsApi';
import type { AnalyticsData } from './api/analyticsApi';
import { systemApi } from './api/systemApi';
import type { SystemStatus } from './api/systemApi';
import { demoApi } from './api/demoApi';

export default function App() {
  // Navigation & States
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [company, setCompany] = useState<Company | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  
  // Lists & Selections
  const [assets, setAssets] = useState<Asset[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [selectedOppId, setSelectedOppId] = useState<string | null>(null);
  const [selectedOppDetail, setSelectedOppDetail] = useState<OpportunityDetail | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [compareData, setCompareData] = useState<CompareResponse[]>([]);
  
  // Loading & Processing States
  const [loadingAssets, setLoadingAssets] = useState<boolean>(false);
  const [loadingOpps, setLoadingOpps] = useState<boolean>(false);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [activeJob, setActiveJob] = useState<ProcessingJob | null>(null);
  
  // Interactive UI Inputs
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null);
  const [uploadDept, setUploadDept] = useState<string>('Operations');
  const [uploadSource, setUploadSource] = useState<string>('Internal Document');
  const [uploading, setUploading] = useState<boolean>(false);
  
  // Human Validator inputs
  const [valMarket, setValMarket] = useState<number>(50);
  const [valFeas, setValFeas] = useState<number>(50);
  const [valStrat, setValStrat] = useState<number>(50);
  const [valReuse, setValReuse] = useState<number>(50);
  const [valConf, setValConf] = useState<number>(50);
  const [valComments, setValComments] = useState<string>('');
  const [valStatus, setValStatus] = useState<string>('pending');
  const [adjustedScore, setAdjustedScore] = useState<number>(50);
  const [adjustmentExplanation, setAdjustmentExplanation] = useState<string>('');

  // Evidence Explorer Details
  const [selectedEvidenceChunk, setSelectedEvidenceChunk] = useState<OpportunityEvidenceResponse | null>(null);

  // Poll intervals references
  const jobPollRef = useRef<any>(null);
  const statusPollRef = useRef<any>(null);

  // --- INITIAL DATA FETCH ---
  useEffect(() => {
    fetchSystemStatus();
    fetchAnalytics();
    
    // Auto-detect if "FrostLink Logistics" company is registered
    setLoadingAssets(true);
    setLoadingOpps(true);
    companyApi.create("FrostLink Logistics", "Fictional logistics demo workspace.").then(comp => {
      setCompany(comp);
      refreshData(comp.id);
    }).catch(() => {
      // Basic workspace fallback
      setCompany({ id: "demo_company", name: "FrostLink Logistics", created_at: "" });
      refreshData("demo_company");
    });

    // Poll system status every 10s
    statusPollRef.current = setInterval(fetchSystemStatus, 10000);
    return () => {
      if (statusPollRef.current) clearInterval(statusPollRef.current);
      if (jobPollRef.current) clearInterval(jobPollRef.current);
    };
  }, []);

  const refreshData = async (companyId: string) => {
    try {
      setLoadingAssets(true);
      setLoadingOpps(true);
      const assetList = await assetApi.list(companyId);
      setAssets(assetList);
      setLoadingAssets(false);
      
      const oppList = await opportunityApi.list(companyId);
      setOpportunities(oppList);
      setLoadingOpps(false);
      
      fetchAnalytics();
    } catch (e) {
      console.error("Failed to load company stats: ", e);
      setLoadingAssets(false);
      setLoadingOpps(false);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const status = await systemApi.getStatus();
      setSystemStatus(status);
    } catch (e) {
      console.error("Failed to fetch system diagnostic status", e);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const data = await analyticsApi.get();
      setAnalytics(data);
    } catch (e) {
      console.error("Failed to load analytics metrics", e);
    }
  };

  // --- JOB POLLING MECHANISMS ---
  const startJobPolling = (jobId: string) => {
    if (jobPollRef.current) clearInterval(jobPollRef.current);
    
    jobPollRef.current = setInterval(async () => {
      try {
        const job = await processingApi.getStatus(jobId);
        setActiveJob(job);
        
        if (job.status === 'completed') {
          if (jobPollRef.current) clearInterval(jobPollRef.current);
          setActiveJob(null);
          if (job.company_id && (!company || company.id !== job.company_id)) {
            companyApi.create("FrostLink Logistics", "Fictional logistics demo workspace.").then(comp => {
              setCompany(comp);
              refreshData(comp.id);
            });
          } else if (company) {
            refreshData(company.id);
          }
          setActiveTab('opportunities');
        } else if (job.status === 'failed') {
          if (jobPollRef.current) clearInterval(jobPollRef.current);
          alert(`Job failed: ${job.error_message}`);
          setActiveJob(null);
        }
      } catch (e) {
        console.error("Polling job status failed: ", e);
      }
    }, 1200);
  };

  // --- DEMO LOADER ---
  const handleLoadDemo = async () => {
    try {
      setActiveTab('discovery');
      const job = await demoApi.load();
      setActiveJob(job);
      startJobPolling(job.id);
    } catch (e) {
      alert("Failed to queue demo load job.");
      console.error(e);
      setActiveTab('overview');
    }
  };

  // --- UPLOAD PIPELINE ---
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFiles || uploadFiles.length === 0 || !company) return;
    setUploading(true);
    
    try {
      for (let i = 0; i < uploadFiles.length; i++) {
        await assetApi.upload(company.id, uploadFiles[i], uploadDept, uploadSource);
      }
      setUploadFiles(null);
      refreshData(company.id);
      alert("Asset(s) uploaded and indexed successfully.");
    } catch (e) {
      alert("File upload failed. Ensure MIME/size limitations are valid.");
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteAsset = async (id: string) => {
    if (!confirm("Are you sure you want to delete this asset? This will delete all chunks and vector indices.")) return;
    try {
      await assetApi.delete(id);
      if (company) refreshData(company.id);
    } catch (e) {
      alert("Failed to delete asset.");
    }
  };

  // --- DISCOVERY RUN ---
  const handleRunDiscovery = async () => {
    if (!company) return;
    try {
      setActiveTab('discovery');
      const job = await discoveryApi.start(company.id);
      setActiveJob(job);
      startJobPolling(job.id);
    } catch (e) {
      alert("Failed to dispatch discovery workflow.");
    }
  };

  // --- OPPORTUNITY VIEWER ---
  const handleSelectOpportunity = async (oppId: string) => {
    setSelectedOppId(oppId);
    setLoadingDetail(true);
    try {
      const detail = await opportunityApi.get(oppId);
      setSelectedOppDetail(detail);
      
      // Load validator defaults
      setValMarket(detail.market_potential);
      setValFeas(detail.feasibility);
      setValStrat(detail.strategic_fit);
      setValReuse(detail.asset_reusability);
      setValConf(detail.confidence);
      setValStatus(detail.status);
      setValComments('');
      
      // Select first evidence chunk by default
      if (detail.evidence && detail.evidence.length > 0) {
        setSelectedEvidenceChunk(detail.evidence[0]);
      } else {
        setSelectedEvidenceChunk(null);
      }
      
      setActiveTab('details');
      setLoadingDetail(false);
    } catch (e) {
      alert("Failed to load opportunity details.");
      setLoadingDetail(false);
    }
  };

  // --- HUMAN VALIDATOR RECALCULATION ---
  useEffect(() => {
    // Math weights formula:
    // (Market Potential * 0.25) + (Feasibility * 0.25) + (Strategic Fit * 0.20) + (Asset Reusability * 0.15) + (Confidence * 0.15)
    const newScore = (valMarket * 0.25) + (valFeas * 0.25) + (valStrat * 0.20) + (valReuse * 0.15) + (valConf * 0.15);
    setAdjustedScore(parseFloat(newScore.toFixed(1)));
    
    if (selectedOppDetail) {
      const diff = newScore - selectedOppDetail.overall_score;
      let text = `Overall score shifted from ${selectedOppDetail.overall_score} to ${newScore.toFixed(1)} (Difference: ${diff > 0 ? '+' : ''}${diff.toFixed(1)} points).`;
      
      const shifts: string[] = [];
      if (valMarket !== selectedOppDetail.market_potential) shifts.push('market potential');
      if (valFeas !== selectedOppDetail.feasibility) shifts.push('feasibility');
      if (valStrat !== selectedOppDetail.strategic_fit) shifts.push('strategic fit');
      if (valReuse !== selectedOppDetail.asset_reusability) shifts.push('asset reusability');
      if (valConf !== selectedOppDetail.confidence) shifts.push('confidence');
      
      if (shifts.length > 0) {
        text += ` Adjustment affected: ${shifts.join(', ')}.`;
      }
      setAdjustmentExplanation(text);
    }
  }, [valMarket, valFeas, valStrat, valReuse, valConf, selectedOppDetail]);

  const handleSaveValidation = async () => {
    if (!selectedOppDetail) return;
    try {
      await validationApi.validate(selectedOppDetail.id, {
        market_potential: valMarket,
        feasibility: valFeas,
        strategic_fit: valStrat,
        asset_reusability: valReuse,
        confidence: valConf,
        comments: valComments,
        status: valStatus
      });
      alert("Scoring recalculation committed successfully.");
      handleSelectOpportunity(selectedOppDetail.id);
    } catch (e) {
      alert("Failed to save scoring validations.");
    }
  };

  const handleStatusChange = async (status: 'APPROVED' | 'REJECTED') => {
    if (!selectedOppDetail) return;
    try {
      if (status === 'APPROVED') {
        await opportunityApi.approve(selectedOppDetail.id);
      } else {
        await opportunityApi.reject(selectedOppDetail.id);
      }
      alert(`Opportunity marked as ${status}.`);
      handleSelectOpportunity(selectedOppDetail.id);
      if (company) refreshData(company.id);
    } catch (e) {
      alert("Failed to update status.");
    }
  };

  // --- COMPARE SELECTION ---
  const toggleCompareSelect = (id: string) => {
    if (compareIds.includes(id)) {
      setCompareIds(compareIds.filter(x => x !== id));
    } else {
      if (compareIds.length >= 4) {
        alert("Maximum of 4 opportunities can be compared simultaneously.");
        return;
      }
      setCompareIds([...compareIds, id]);
    }
  };

  const handleCompareTrigger = async () => {
    if (compareIds.length < 2) {
      alert("Select at least 2 opportunities to compare.");
      return;
    }
    try {
      const result = await opportunityApi.compare(compareIds);
      setCompareData(result);
      setActiveTab('compare');
    } catch (e) {
      alert("Compare routing failed.");
    }
  };

  // --- RENDER SERVICES HEALTH DOT ---
  const renderHealthDot = (svc: string) => {
    if (!systemStatus) return <span className="h-2 w-2 rounded-full bg-slate-600 animate-pulse inline-block mr-1.5"></span>;
    const item = systemStatus[svc as keyof SystemStatus];
    if (!item) return <span className="h-2 w-2 rounded-full bg-slate-650 inline-block mr-1.5"></span>;
    
    if (item.status === 'ONLINE') {
      return <span className="h-2 w-2 rounded-full bg-green-500 shadow-sm shadow-green-500/50 inline-block mr-1.5" title="ONLINE"></span>;
    } else if (item.status === 'DEGRADED') {
      return <span className="h-2 w-2 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50 inline-block mr-1.5" title="DEGRADED"></span>;
    } else {
      return <span className="h-2 w-2 rounded-full bg-red-500 shadow-sm shadow-red-500/50 inline-block mr-1.5" title="OFFLINE"></span>;
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#020617] text-[#f8fafc] overflow-hidden antialiased">
      
      {/* --- SIDEBAR --- */}
      <div className={`glass-panel border-r border-slate-800/80 transition-all duration-300 flex flex-col h-full bg-slate-950/70 ${sidebarCollapsed ? 'w-20' : 'w-64'}`}>
        {/* Brand logo header */}
        <div className="p-5 border-b border-slate-800/80 flex items-center justify-between h-20">
          {!sidebarCollapsed && (
            <div className="flex flex-col">
              <span className="font-black text-xl tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400">INTRACAPITAL</span>
              <span className="text-[9px] uppercase tracking-widest text-slate-400 font-bold block mt-0.5">AI Venture Intelligence</span>
            </div>
          )}
          <button onClick={() => setSidebarCollapsed(!sidebarCollapsed)} className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-855 border border-slate-800 text-slate-400 hover:text-white transition-colors duration-200 mx-auto">
            {sidebarCollapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
          {[
            { id: 'overview', label: 'Overview', icon: Building2 },
            { id: 'assets', label: 'Company Assets', icon: FileText },
            { id: 'discovery', label: 'Discovery Pipeline', icon: Activity },
            { id: 'opportunities', label: 'Opportunities', icon: Compass },
            { id: 'evidence', label: 'Evidence Explorer', icon: Eye },
            { id: 'business_model', label: 'Business Models', icon: Layers },
            { id: 'validator', label: 'Validator', icon: Sliders },
            { id: 'compare', label: 'Compare Matrix', icon: CheckSquare },
            { id: 'analytics', label: 'Analytics Charts', icon: BarChart3 },
            { id: 'architecture', label: 'Architecture Flow', icon: Brain },
            { id: 'system', label: 'System status', icon: HelpCircle }
          ].map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button 
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center p-3 rounded-xl text-sm transition-all duration-200 group relative ${active ? 'bg-gradient-to-r from-blue-600/25 to-cyan-600/10 text-white font-semibold border border-blue-500/25' : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-100'}`}
              >
                <Icon size={18} className={`flex-shrink-0 transition-transform duration-200 group-hover:scale-110 ${active ? 'text-blue-400' : 'text-slate-400'}`} />
                {!sidebarCollapsed && <span className="ml-3 truncate">{item.label}</span>}
                {active && (
                  <span className="absolute left-0 top-3 bottom-3 w-1 rounded-r bg-blue-500"></span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Live Granite Status Footer */}
        <div className="p-5 border-t border-slate-800/80 text-slate-500 flex flex-col space-y-2 h-20 justify-center">
          <div className="flex items-center text-xs font-semibold text-slate-400">
            {renderHealthDot('ollama')}
            {!sidebarCollapsed && (
              <span className="truncate tracking-wide">
                {systemStatus?.ollama.status === 'ONLINE' ? 'LIVE IBM GRANITE' : 'LOCAL MOCKS ONLINE'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* --- MAIN PAGE GATEWAY --- */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* Top Header bar */}
        <header className="h-20 border-b border-slate-850 flex items-center justify-between px-8 bg-slate-950/30 backdrop-blur-md">
          <div className="flex items-center space-x-3">
            <span className="text-slate-450 text-[10px] font-bold uppercase tracking-wider">Enterprise Tenant:</span>
            <div className="bg-slate-900 border border-slate-800 px-4 py-1.5 rounded-xl text-sm font-extrabold flex items-center shadow-inner text-slate-100">
              <span className="h-2 w-2 rounded-full bg-blue-500 mr-2.5 shadow-sm shadow-blue-500/50"></span>
              {company?.name || 'FrostLink Logistics'}
            </div>
          </div>

          <div className="flex items-center space-x-5">
            <div className="flex items-center space-x-3 bg-slate-900/40 px-5 py-2 rounded-full border border-slate-800 text-[11px] text-slate-400 font-bold">
              <span className="flex items-center">{renderHealthDot('fastapi')} API</span>
              <span className="flex items-center">{renderHealthDot('qdrant')} Qdrant</span>
              <span className="flex items-center">{renderHealthDot('neo4j')} Neo4j</span>
              <span className="flex items-center">{renderHealthDot('ollama')} Ollama</span>
            </div>
            
            <button onClick={handleLoadDemo} className="px-5 py-2.5 bg-gradient-to-r from-purple-650 to-indigo-650 hover:from-purple-550 hover:to-indigo-550 text-xs font-extrabold rounded-xl border border-purple-550 shadow-md shadow-purple-950/20 active:scale-95 transition-all duration-150">
              [ LOAD DEMO COMPANY ]
            </button>
          </div>
        </header>

        {/* Content Viewer container */}
        <main className="flex-1 p-8 overflow-y-auto bg-[#020617]">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
              className="h-full"
            >
              
              {/* === OVERVIEW TAB === */}
              {activeTab === 'overview' && (
                <div className="space-y-8">
                  {/* Hero Jumbotron text headers */}
                  <div className="bg-gradient-to-br from-slate-950/80 to-slate-900/40 p-10 rounded-2xl border border-slate-800/80 relative overflow-hidden glass-panel">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl -z-10"></div>
                    <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl -z-10"></div>
                    
                    <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-3 text-slate-100">Discover Businesses Hidden Inside Businesses.</h1>
                    <p className="text-slate-400 text-lg max-w-3xl mb-8 leading-relaxed">
                      Turn overlooked company assets, customer signals, logistics records and operational database telemetry into your next high-margin business opportunities, SaaS models, or technology spin-offs.
                    </p>
                    
                    <div className="flex items-center space-x-4">
                      <button onClick={handleRunDiscovery} className="px-6 py-3.5 bg-blue-650 hover:bg-blue-550 text-sm font-extrabold rounded-xl flex items-center transition-all duration-200 active:scale-95 shadow-lg shadow-blue-900/35 border border-blue-500">
                        Discover Hidden Opportunities <ArrowRight size={16} className="ml-2.5" />
                      </button>
                      <button onClick={() => setActiveTab('assets')} className="px-6 py-3.5 bg-slate-900/80 border border-slate-800 hover:bg-slate-800 text-sm font-bold rounded-xl transition-all duration-200 active:scale-95">
                        Manage Raw Assets
                      </button>
                    </div>
                  </div>

                  {/* Summary Metric Stats Grids */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                    {[
                      { label: 'Raw Data Files', value: analytics?.processed_assets ?? 0, icon: FileText, color: 'text-blue-400' },
                      { label: 'Extracted Links', value: analytics?.total_connections ?? 0, icon: Brain, color: 'text-purple-400' },
                      { label: 'Identified Options', value: analytics?.total_opportunities ?? 0, icon: Compass, color: 'text-cyan-400' },
                      { label: 'Discovery Confidence', value: `${analytics?.average_confidence ?? 0}%`, icon: ShieldCheck, color: 'text-green-400' }
                    ].map((card, idx) => {
                      const CardIcon = card.icon;
                      return (
                        <div key={idx} className="glass-panel p-6 rounded-xl border border-slate-800 flex items-center space-x-4">
                          <div className={`p-3 bg-slate-900 rounded-xl ${card.color} border border-slate-800`}>
                            <CardIcon size={24} />
                          </div>
                          <div>
                            <span className="text-[10px] uppercase text-slate-400 tracking-wider font-extrabold block">{card.label}</span>
                            <span className="text-3xl font-black text-white block mt-1 font-mono">{card.value}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Engine Animation Visualizer */}
                  <div className="glass-panel p-8 rounded-xl border border-slate-800 flex flex-col items-center">
                    <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-8 border-b border-slate-850 pb-2 w-full text-center">Engine Relational Network</h3>
                    <div className="relative w-full max-w-[650px] h-[340px] flex items-center justify-center">
                      
                      {/* SVGs node connections */}
                      <svg className="absolute inset-0 w-full h-full pointer-events-none">
                        <line x1="50%" y1="50%" x2="20%" y2="25%" stroke="#3b82f6" strokeWidth="1" strokeDasharray="5,5" className="animate-pulse" />
                        <line x1="50%" y1="50%" x2="80%" y2="25%" stroke="#06b6d4" strokeWidth="1" strokeDasharray="5,5" />
                        <line x1="50%" y1="50%" x2="15%" y2="70%" stroke="#8b5cf6" strokeWidth="1" strokeDasharray="5,5" />
                        <line x1="50%" y1="50%" x2="85%" y2="70%" stroke="#10b981" strokeWidth="1" strokeDasharray="5,5" />
                        <line x1="50%" y1="50%" x2="50%" y2="15%" stroke="#f59e0b" strokeWidth="1" strokeDasharray="5,5" />
                      </svg>

                      {/* Rotating Center node */}
                      <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 25, ease: 'linear' }}
                        className="h-28 w-28 rounded-full bg-gradient-to-tr from-blue-600 via-cyan-500 to-purple-600 absolute flex items-center justify-center p-0.5 z-10 shadow-lg shadow-blue-500/25"
                      >
                        <div className="h-full w-full rounded-full bg-slate-950 flex flex-col items-center justify-center p-2 text-center">
                          <Brain size={24} className="text-cyan-400 animate-pulse mb-1" />
                          <span className="text-[9px] font-black tracking-widest text-cyan-450">GRANITE AI</span>
                          <span className="text-[8px] uppercase tracking-wide text-slate-400">ENGINE</span>
                        </div>
                      </motion.div>

                      {/* Orbiting Satellite nodes */}
                      {[
                        { label: 'PATENTS', top: '15%', left: '12%', color: 'border-blue-500/30 text-blue-400 shadow-blue-500/5' },
                        { label: 'RESEARCH', top: '5%', left: '44%', color: 'border-amber-500/30 text-amber-400 shadow-amber-500/5' },
                        { label: 'CUSTOMER LOGS', top: '15%', left: '72%', color: 'border-cyan-500/30 text-cyan-400 shadow-cyan-500/5' },
                        { label: 'OPERATIONS', top: '62%', left: '5%', color: 'border-purple-500/30 text-purple-400 shadow-purple-500/5' },
                        { label: 'SENSOR telemetry', top: '62%', left: '76%', color: 'border-green-500/30 text-green-400 shadow-green-500/5' }
                      ].map((sat, idx) => (
                        <div 
                          key={idx} 
                          className={`absolute px-4 py-2 border rounded-full bg-slate-950 font-bold text-[10px] tracking-widest ${sat.color} shadow-lg flex items-center justify-center hover:scale-105 hover:border-white/30 transition-all duration-200 cursor-pointer`}
                          style={{ top: sat.top, left: sat.left }}
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-current mr-2 animate-ping"></span>
                          {sat.label}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* === COMPANY ASSETS TAB === */}
              {activeTab === 'assets' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  
                  {/* Left Upload Form Panel */}
                  <div className="lg:col-span-1 space-y-6">
                    <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/45">
                      <h3 className="font-black text-xs uppercase tracking-widest mb-5 flex items-center border-b border-slate-850 pb-2"><Upload size={14} className="text-blue-450 mr-2" /> Index Raw Assets</h3>
                      
                      <form onSubmit={handleUpload} className="space-y-5">
                        <div className="border-2 border-dashed border-slate-800 hover:border-blue-500/30 rounded-xl p-8 text-center cursor-pointer transition-colors duration-200 bg-slate-900/10">
                          <input 
                            type="file" 
                            multiple 
                            onChange={(e) => setUploadFiles(e.target.files)} 
                            className="hidden" 
                            id="file-upload" 
                          />
                          <label htmlFor="file-upload" className="cursor-pointer block space-y-3">
                            <Upload className="mx-auto text-slate-500" size={32} />
                            <span className="text-sm font-semibold block text-slate-355">Choose files from local drive</span>
                            <span className="text-[10px] text-slate-500 block leading-normal">PDF, DOCX, TXT, CSV, XLSX, JSON (Max 100MB)</span>
                          </label>
                        </div>

                        {uploadFiles && uploadFiles.length > 0 && (
                          <div className="bg-slate-900/40 p-4 rounded-lg border border-slate-850 text-xs space-y-1.5">
                            <span className="font-extrabold text-slate-400 block mb-1">Queue ({uploadFiles.length}):</span>
                            {Array.from(uploadFiles).map((f, i) => (
                              <div key={i} className="text-slate-300 truncate font-mono">• {f.name} ({(f.size / 1024).toFixed(1)} KB)</div>
                            ))}
                          </div>
                        )}

                        <div className="space-y-1">
                          <label className="text-[10px] font-extrabold text-slate-450 block uppercase tracking-wider">Business Department</label>
                          <select value={uploadDept} onChange={(e) => setUploadDept(e.target.value)} className="w-full bg-slate-900 border border-slate-800 p-3 rounded-lg text-xs font-semibold text-slate-200 focus:outline-none focus:border-blue-500">
                            <option>Operations</option>
                            <option>Logistics</option>
                            <option>Maintenance</option>
                            <option>Quality Assurance</option>
                            <option>R&D</option>
                          </select>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[10px] font-extrabold text-slate-455 block uppercase tracking-wider">Source Origin</label>
                          <input type="text" value={uploadSource} onChange={(e) => setUploadSource(e.target.value)} className="w-full bg-slate-900 border border-slate-800 p-3 rounded-lg text-xs focus:outline-none focus:border-blue-500 text-slate-200" placeholder="e.g. Audit Logs" />
                        </div>

                        <button 
                          type="submit" 
                          disabled={uploading || !uploadFiles}
                          className="w-full py-3 bg-blue-650 hover:bg-blue-550 disabled:bg-slate-900 disabled:text-slate-600 disabled:border-slate-850 font-bold rounded-xl transition-all duration-150 flex items-center justify-center text-xs uppercase tracking-wider border border-blue-600/30"
                        >
                          {uploading ? <RefreshCw className="animate-spin mr-2" size={14} /> : null}
                          Upload & Chunker
                        </button>
                      </form>
                    </div>
                  </div>

                  {/* Right Uploaded Assets table */}
                  <div className="lg:col-span-2">
                    <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden h-full flex flex-col">
                      <div className="p-5 border-b border-slate-850 flex items-center justify-between">
                        <h3 className="font-black text-xs uppercase tracking-widest text-slate-400 flex items-center"><FileText size={14} className="text-cyan-500 mr-2" /> Registered Asset Documents</h3>
                        <span className="text-[10px] bg-slate-900 px-3 py-1 border border-slate-800 rounded-full font-bold text-slate-400">{assets.length} Files</span>
                      </div>
                      
                      <div className="flex-1 overflow-x-auto">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead>
                            <tr className="border-b border-slate-850 text-slate-450 font-bold uppercase bg-slate-950/20">
                              <th className="p-4 w-1/3">File Name</th>
                              <th className="p-4">Format</th>
                              <th className="p-4">Dept</th>
                              <th className="p-4">Pipeline Status</th>
                              <th className="p-4 text-center">Trash</th>
                            </tr>
                          </thead>
                          <tbody>
                            {loadingAssets ? (
                              // Animated placeholder row
                              [1, 2, 3].map(i => (
                                <tr key={i} className="border-b border-slate-850 animate-pulse">
                                  <td className="p-4"><div className="h-3 bg-slate-900 rounded w-48"></div></td>
                                  <td className="p-4"><div className="h-3 bg-slate-900 rounded w-12"></div></td>
                                  <td className="p-4"><div className="h-3 bg-slate-900 rounded w-16"></div></td>
                                  <td className="p-4"><div className="h-4 bg-slate-900 rounded w-20"></div></td>
                                  <td className="p-4 text-center"><div className="h-6 bg-slate-900 rounded w-8 mx-auto"></div></td>
                                </tr>
                              ))
                            ) : assets.length === 0 ? (
                              <tr>
                                <td colSpan={5} className="p-16 text-center text-slate-500 font-semibold italic">
                                  No raw documents uploaded yet. Populate using load demo.
                                </td>
                              </tr>
                            ) : (
                              assets.map((asset) => (
                                <tr key={asset.id} className="border-b border-slate-850/60 hover:bg-slate-900/20 transition-colors">
                                  <td className="p-4 font-bold text-slate-100 truncate max-w-64">{asset.file_name}</td>
                                  <td className="p-4 font-mono font-bold text-slate-400">{asset.asset_type}</td>
                                  <td className="p-4 text-slate-400 font-medium">{asset.department || 'Operations'}</td>
                                  <td className="p-4">
                                    <span className={`px-2.5 py-0.5 text-[9px] font-extrabold rounded-full border ${
                                      asset.status === 'PROCESSED' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
                                      asset.status === 'PROCESSING' ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400 animate-pulse' :
                                      asset.status === 'UPLOADED' ? 'bg-blue-500/10 border-blue-500/30 text-blue-400' :
                                      'bg-red-500/10 border-red-500/30 text-red-400'
                                    }`}>
                                      {asset.status}
                                    </span>
                                  </td>
                                  <td className="p-4 text-center">
                                    <button onClick={() => handleDeleteAsset(asset.id)} className="p-1.5 text-slate-400 hover:text-red-400 rounded-lg bg-slate-900 hover:bg-slate-850 border border-slate-800 transition-colors">
                                      <Trash2 size={13} />
                                    </button>
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* === DISCOVERY PIPELINE TAB === */}
              {activeTab === 'discovery' && (
                <div className="max-w-2xl mx-auto space-y-6">
                  <div className="glass-panel p-8 rounded-xl border border-slate-800 text-center">
                    <Activity size={48} className="mx-auto text-blue-500 mb-4 animate-pulse" />
                    <h2 className="text-2xl font-extrabold mb-1">Autonomous Venture Engine</h2>
                    <p className="text-slate-400 text-sm max-w-md mx-auto">
                      INTRACAPITAL is parsing evidence logs, mapping technology networks, and invoking Granite local LLM models to identify opportunities.
                    </p>

                    <div className="mt-8 space-y-6 text-left max-w-md mx-auto">
                      {[
                        { step: '01', title: 'Understanding Assets', desc: 'Docling structure extracting and Excel data summaries.' },
                        { step: '02', title: 'Retrieving Evidence', desc: 'Fetching semantic top-K vectors from Qdrant.' },
                        { step: '03', title: 'Connecting Signals', desc: 'Mapping relational links in SQLite Knowledge Graph.' },
                        { step: '04', title: 'Granite Analysis', desc: 'Local model running cross-domain diagnostics.' },
                        { step: '05', title: 'Evaluating Opportunities', desc: 'Recalculating feasibility,Strategic fit, confidence scores.' },
                        { step: '06', title: 'Ranking Results', desc: 'Generating Canvas plans and database records.' }
                      ].map((step, idx) => {
                        const isJobRunning = activeJob !== null;
                        const currentStepName = activeJob?.current_step || '';
                        
                        let stepStatus: 'pending' | 'running' | 'completed' = 'pending';
                        if (isJobRunning) {
                          const currentStepNum = parseInt(currentStepName.substring(0, 2)) || 0;
                          const thisStepNum = idx + 1;
                          if (thisStepNum < currentStepNum) {
                            stepStatus = 'completed';
                          } else if (thisStepNum === currentStepNum) {
                            stepStatus = 'running';
                          }
                        }

                        return (
                          <div key={idx} className="flex items-start space-x-4">
                            <div className={`h-8 w-8 rounded-full border flex items-center justify-center text-xs font-bold font-mono transition-colors duration-205 ${
                              stepStatus === 'completed' ? 'bg-green-500/10 border-green-500 text-green-400' :
                              stepStatus === 'running' ? 'bg-blue-500/10 border-blue-500 text-blue-400 animate-pulse' :
                              'bg-slate-900 border-slate-800 text-slate-500'
                            }`}>
                              {stepStatus === 'completed' ? <CheckCircle2 size={16} /> : step.step}
                            </div>
                            <div className="flex-1">
                              <span className={`font-bold block text-sm ${
                                stepStatus === 'running' ? 'text-blue-400' :
                                stepStatus === 'completed' ? 'text-slate-100' : 'text-slate-550'
                              }`}>{step.title}</span>
                              <span className="text-[11px] text-slate-400 block mt-0.5">{step.desc}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {activeJob && (
                      <div className="mt-8 space-y-2">
                        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                          <span>Progress: {activeJob.progress}%</span>
                          <span>Elapsed: {activeJob.elapsed_time.toFixed(1)}s</span>
                        </div>
                        <div className="h-2.5 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-850">
                          <div className="h-full bg-gradient-to-r from-blue-600 to-cyan-550 transition-all duration-300" style={{ width: `${activeJob.progress}%` }}></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* === OPPORTUNITIES TAB === */}
              {activeTab === 'opportunities' && (
                <div className="space-y-6">
                  
                  {/* Sorting Header */}
                  <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <h2 className="text-xl font-black">Identified Opportunities</h2>
                      <p className="text-slate-450 text-xs mt-0.5">Venture models extracted from localized data metrics.</p>
                    </div>

                    <div className="flex items-center space-x-3">
                      <button onClick={handleRunDiscovery} className="px-4 py-2 bg-slate-900/60 border border-slate-800 hover:bg-slate-800 rounded-xl text-xs font-semibold flex items-center transition-colors active:scale-95">
                        <RefreshCw size={12} className="mr-2" /> Recalculate options
                      </button>
                      {compareIds.length >= 2 && (
                        <button onClick={handleCompareTrigger} className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-505 rounded-xl text-xs font-black flex items-center border border-blue-500/25 shadow shadow-blue-500/10 transition-all active:scale-95">
                          Compare side-by-side ({compareIds.length})
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Opportunities Grids */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {loadingOpps ? (
                      [1, 2, 3].map(i => (
                        <div key={i} className="glass-panel rounded-xl border border-slate-800 p-6 space-y-4 animate-pulse">
                          <div className="flex justify-between items-start">
                            <div className="space-y-1.5"><div className="h-3 bg-slate-900 rounded w-16"></div><div className="h-5 bg-slate-900 rounded w-36"></div></div>
                            <div className="h-8 bg-slate-900 rounded w-8"></div>
                          </div>
                          <div className="h-16 bg-slate-900 rounded"></div>
                          <div className="space-y-2"><div className="h-2 bg-slate-900 rounded"></div><div className="h-2 bg-slate-900 rounded"></div></div>
                        </div>
                      ))
                    ) : opportunities.length === 0 ? (
                      <div className="col-span-full glass-panel p-16 text-center text-slate-500 font-semibold italic">
                        No venture opportunities identified. Click load demo or start discovery.
                      </div>
                    ) : (
                      opportunities.map((opp, idx) => (
                        <div key={opp.id} className="glass-panel rounded-xl border border-slate-800/80 hover:border-slate-700 bg-slate-950/20 transition-all duration-200 flex flex-col overflow-hidden">
                          
                          {/* Card header */}
                          <div className="p-6 border-b border-slate-850 flex items-start justify-between">
                            <div>
                              <span className="text-[9px] font-mono font-bold uppercase text-slate-400">RANK 0{idx+1} • {opp.industry}</span>
                              <h3 className="font-bold text-md text-white mt-1 hover:text-blue-400 cursor-pointer transition-colors leading-snug" onClick={() => handleSelectOpportunity(opp.id)}>{opp.title}</h3>
                            </div>
                            
                            <div className="flex flex-col items-end">
                              <span className="text-xl font-black text-cyan-400 font-mono leading-none">{opp.overall_score}</span>
                              <span className="text-[8px] uppercase tracking-wider text-slate-400 font-bold block mt-1">Score</span>
                            </div>
                          </div>

                          {/* Card body */}
                          <div className="p-6 flex-1 space-y-5">
                            <p className="text-slate-400 text-xs leading-relaxed line-clamp-3">{opp.short_description}</p>
                            
                            {/* Score bars previews */}
                            <div className="space-y-2.5 bg-slate-900/30 p-4 rounded-xl border border-slate-850/50">
                              {[
                                { label: 'Market Potential', val: opp.market_potential, color: 'bg-blue-500' },
                                { label: 'Feasibility', val: opp.feasibility, color: 'bg-amber-500' },
                                { label: 'Strategic Fit', val: opp.strategic_fit, color: 'bg-purple-500' },
                                { label: 'Confidence', val: opp.confidence, color: 'bg-green-500' }
                              ].map((bar, i) => (
                                <div key={i} className="space-y-1">
                                  <div className="flex items-center justify-between text-[9px] font-bold text-slate-400">
                                    <span>{bar.label}</span>
                                    <span>{bar.val}/100</span>
                                  </div>
                                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                    <div className={`h-full ${bar.color}`} style={{ width: `${bar.val}%` }}></div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Card footer */}
                          <div className="p-4 bg-slate-950/40 border-t border-slate-850 flex items-center justify-between">
                            <label className="flex items-center text-xs text-slate-450 cursor-pointer font-semibold select-none">
                              <input 
                                type="checkbox" 
                                checked={compareIds.includes(opp.id)} 
                                onChange={() => toggleCompareSelect(opp.id)} 
                                className="mr-2.5 accent-blue-500 h-4 w-4 rounded border-slate-800 bg-slate-900"
                              />
                              Select to Compare
                            </label>
                            
                            <button onClick={() => handleSelectOpportunity(opp.id)} className="px-4 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-850 hover:text-white rounded-lg text-xs font-bold transition-all active:scale-95">
                              View Details
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* === OPPORTUNITY DETAILS TAB === */}
              {activeTab === 'details' && selectedOppDetail && (
                loadingDetail ? (
                  <div className="glass-panel p-16 rounded-xl border border-slate-800 text-center animate-pulse">
                    <RefreshCw className="animate-spin mx-auto text-blue-500 mb-4" size={32} />
                    <h3 className="text-md font-bold text-white mb-1">Loading Venture Details</h3>
                    <p className="text-xs text-slate-500">Querying RAG vectors and SQLite records...</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Detail Title Header card */}
                    <div className="glass-panel p-6 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6 bg-slate-950/20">
                      <div>
                        <button onClick={() => setActiveTab('opportunities')} className="text-[11px] text-slate-455 hover:text-white font-bold mb-2.5 block transition-colors">← Back to Opportunities</button>
                        <span className="text-[9px] font-bold uppercase text-slate-400 tracking-wider">AI-generated demo opportunity • {selectedOppDetail.industry}</span>
                        <h2 className="text-2xl font-black text-white mt-1 leading-snug">{selectedOppDetail.title}</h2>
                      </div>

                      <div className="flex items-center space-x-5">
                        <div className="text-center bg-slate-900 border border-slate-800 px-6 py-3 rounded-xl shadow-inner">
                          <span className="text-3xl font-black text-cyan-400 font-mono block leading-none">{selectedOppDetail.overall_score}</span>
                          <span className="text-[9px] uppercase tracking-widest text-slate-400 font-extrabold block mt-1.5">Score</span>
                        </div>
                        
                        <div className="flex flex-col space-y-2">
                          <button onClick={() => handleStatusChange('APPROVED')} className="px-4 py-2 bg-green-600 hover:bg-green-550 text-xs font-bold rounded-lg border border-green-500 shadow active:scale-95 transition-all">
                            Approve Opportunity
                          </button>
                          <button onClick={() => handleStatusChange('REJECTED')} className="px-4 py-2 bg-red-600 hover:bg-red-550 text-xs font-bold rounded-lg border border-red-500 shadow active:scale-95 transition-all">
                            Reject Opportunity
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Sub Grid splits: Left details / Right radar & BMC */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      
                      {/* Left Column: Metrics & textual descriptions */}
                      <div className="lg:col-span-2 space-y-6">
                        
                        {/* Criteria Score Breakdowns */}
                        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-5 bg-slate-950/15">
                          <h3 className="font-black text-xs uppercase tracking-widest text-slate-400 border-b border-slate-850 pb-2">Venture Score Breakdown</h3>
                          
                          <div className="space-y-4">
                            {[
                              { label: 'Market Potential', val: selectedOppDetail.market_potential, weight: '25%', color: 'bg-blue-500' },
                              { label: 'Feasibility', val: selectedOppDetail.feasibility, weight: '25%', color: 'bg-amber-500' },
                              { label: 'Strategic Fit', val: selectedOppDetail.strategic_fit, weight: '20%', color: 'bg-purple-500' },
                              { label: 'Asset Reusability', val: selectedOppDetail.asset_reusability, weight: '15%', color: 'bg-cyan-500' },
                              { label: 'Confidence Score', val: selectedOppDetail.confidence, weight: '15%', color: 'bg-green-500' }
                            ].map((crit, idx) => (
                              <div key={idx} className="space-y-1.5">
                                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                                  <span>{crit.label} <span className="text-[10px] text-slate-500 font-bold">(Weight: {crit.weight})</span></span>
                                  <span className="font-mono">{crit.val}/105</span>
                                </div>
                                <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-850">
                                  <div className={`h-full ${crit.color}`} style={{ width: `${crit.val}%` }}></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Text details */}
                        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-6">
                          <div>
                            <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-widest block mb-2">Why this Opportunity? (Problem Statement)</h4>
                            <p className="text-slate-300 text-xs leading-relaxed">{selectedOppDetail.problem}</p>
                          </div>
                          <div>
                            <h4 className="text-[10px] font-black text-cyan-400 uppercase tracking-widest block mb-2">Proposed Solution</h4>
                            <p className="text-slate-300 text-xs leading-relaxed">{selectedOppDetail.solution}</p>
                          </div>
                          <div>
                            <h4 className="text-[10px] font-black text-purple-400 uppercase tracking-widest block mb-2">Target Customer Segments</h4>
                            <p className="text-slate-300 text-xs leading-relaxed">{selectedOppDetail.target_customers}</p>
                          </div>
                          <div>
                            <h4 className="text-[10px] font-black text-amber-500 uppercase tracking-widest block mb-2">AI Reasoning narrative</h4>
                            <p className="text-slate-300 text-xs leading-relaxed">{selectedOppDetail.reasoning}</p>
                          </div>
                        </div>
                      </div>

                      {/* Right Column: Radar Chart & Evidence sidebar list */}
                      <div className="lg:col-span-1 space-y-6">
                        
                        {/* Radar charts */}
                        <div className="glass-panel p-6 rounded-xl border border-slate-800 flex flex-col items-center bg-slate-950/15">
                          <h3 className="font-black text-xs uppercase tracking-widest text-slate-405 self-start border-b border-slate-850 pb-2 w-full mb-4">Venture Shape Radar</h3>
                          
                          <div className="w-full h-[220px]">
                            <ResponsiveContainer width="100%" height="100%">
                              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={[
                                { subject: 'Market', value: selectedOppDetail.market_potential },
                                { subject: 'Feas.', value: selectedOppDetail.feasibility },
                                { subject: 'Strategy', value: selectedOppDetail.strategic_fit },
                                { subject: 'Reuse', value: selectedOppDetail.asset_reusability },
                                { subject: 'Conf.', value: selectedOppDetail.confidence }
                              ]}>
                                <PolarGrid stroke="#334155" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                                <Radar name="Venture" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                              </RadarChart>
                            </ResponsiveContainer>
                          </div>
                        </div>

                        {/* Supporting Evidence trace cards */}
                        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
                          <h3 className="font-black text-xs uppercase tracking-widest text-slate-400 border-b border-slate-850 pb-2 block">Citing evidence traces</h3>
                          
                          <div className="space-y-3">
                            {selectedOppDetail.evidence && selectedOppDetail.evidence.length === 0 ? (
                              <span className="text-xs text-slate-505 block italic font-medium">No evidence traces mapped.</span>
                            ) : (
                              selectedOppDetail.evidence.map((ev, i) => (
                                <div key={i} className="bg-slate-900 border border-slate-850 p-4 rounded-xl space-y-2 hover:border-blue-500/20 transition-colors">
                                  <div className="flex items-center justify-between">
                                    <span className="text-[10px] bg-slate-800 px-2.5 py-0.5 border border-slate-750 text-slate-300 font-mono rounded truncate max-w-40">{ev.file_name}</span>
                                    <span className="text-[10px] font-bold text-cyan-400 font-mono">{Math.round(ev.relevance_score * 100)}% Match</span>
                                  </div>
                                  <p className="text-[11px] text-slate-450 leading-relaxed">"{ev.supporting_text}"</p>
                                </div>
                              ))
                            )}
                          </div>
                        </div>

                      </div>
                    </div>
                  </div>
                )
              )}

              {/* === EVIDENCE EXPLORER TAB === */}
              {activeTab === 'evidence' && (
                <div className="space-y-6">
                  
                  {/* Header info */}
                  <div className="glass-panel p-5 rounded-xl border border-slate-800">
                    <h2 className="text-xl font-black">Evidence Connection Explorer</h2>
                    <p className="text-slate-450 text-xs mt-0.5">Visually inspect the physical audit data trace backing our business recommendations.</p>
                  </div>

                  {/* Split Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Left List of Discovered Opportunities */}
                    <div className="lg:col-span-1 space-y-4">
                      <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3">
                        <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-3 border-b border-slate-850 pb-2">Venture Suggestion</h3>
                        <div className="space-y-2">
                          {opportunities.map((opp) => (
                            <button 
                              key={opp.id}
                              onClick={() => handleSelectOpportunity(opp.id)}
                              className={`w-full text-left p-3.5 rounded-xl border text-xs font-bold transition-all duration-150 ${
                                selectedOppId === opp.id ? 'bg-gradient-to-r from-blue-600/35 to-cyan-500/10 border-blue-500 text-white shadow-md' : 'bg-slate-900/40 border-slate-850 text-slate-450 hover:bg-slate-900 hover:text-slate-200'
                              }`}
                            >
                              <div className="flex justify-between items-center">
                                <span className="truncate mr-2">{opp.title}</span>
                                <span className="font-mono text-cyan-400 font-extrabold">{opp.overall_score}</span>
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Right Canvas visualizer & Side panel details */}
                    <div className="lg:col-span-2">
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 h-full flex flex-col justify-between space-y-6">
                        
                        {selectedOppDetail ? (
                          <div className="space-y-6 flex-1 flex flex-col justify-between">
                            {/* Simplified connection network block representation */}
                            <div className="bg-slate-950/80 p-6 rounded-2xl border border-slate-900 flex flex-col items-center justify-center min-h-[200px] relative">
                              <div className="absolute top-3 left-4 text-[9px] uppercase tracking-widest text-slate-500 font-bold">RAG Graph Trace Map</div>
                              
                              <div className="flex flex-col md:flex-row items-center justify-between w-full max-w-md gap-6 mt-4">
                                {/* Left sources */}
                                <div className="space-y-2 flex flex-col">
                                  {selectedOppDetail.evidence.map((ev, i) => (
                                    <div key={i} className="px-3.5 py-1.5 bg-slate-900 border border-slate-800 text-[10px] rounded font-mono text-slate-350 truncate max-w-44 text-center">
                                      {ev.file_name}
                                    </div>
                                  ))}
                                </div>
                                
                                {/* Center Connector line representation */}
                                <div className="flex flex-col items-center">
                                  <ArrowRight className="text-cyan-455 rotate-90 md:rotate-0 animate-pulse" size={24} />
                                  <span className="text-[9px] uppercase tracking-widest text-cyan-500 font-black mt-1">RETRIEVAL</span>
                                </div>

                                {/* Right Opportunity */}
                                <div className="px-4.5 py-3 border border-blue-500 bg-blue-950/20 text-xs font-black text-center rounded-xl shadow shadow-blue-500/10 max-w-44 truncate">
                                  {selectedOppDetail.title}
                                </div>
                              </div>
                            </div>

                            {/* Detailed evidence block info */}
                            <div className="bg-slate-900/30 p-5 rounded-2xl border border-slate-850/60 space-y-3">
                              <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400 border-b border-slate-850 pb-2">Evidence block Details</h4>
                              
                              {selectedEvidenceChunk ? (
                                <div className="space-y-3">
                                  <div className="flex items-center justify-between text-xs">
                                    <span className="font-semibold text-slate-300">File: <code className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-cyan-400 font-mono">{selectedEvidenceChunk.file_name}</code></span>
                                    <span className="font-mono text-slate-500">Match score: {Math.round(selectedEvidenceChunk.relevance_score * 100)}%</span>
                                  </div>
                                  <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-900 text-slate-300 text-xs leading-relaxed italic">
                                    "{selectedEvidenceChunk.supporting_text}"
                                  </div>
                                </div>
                              ) : (
                                <span className="text-xs text-slate-500 block italic font-semibold">Select an opportunity to read detailed chunks.</span>
                              )}
                            </div>
                          </div>
                        ) : (
                          <div className="text-center p-16 text-slate-500 font-semibold italic">
                            Select an opportunity from the list to display its connected database traces.
                          </div>
                        )}
                        
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* === BUSINESS MODEL CANVAS TAB === */}
              {activeTab === 'business_model' && (
                <div className="space-y-6">
                  
                  {/* Selection Header */}
                  <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <h2 className="text-xl font-black">Business Model Canvas</h2>
                      <p className="text-slate-450 text-xs mt-0.5">Explore the generated business plan with clearly demarcated assumptions.</p>
                    </div>

                    <select 
                      value={selectedOppId || ''} 
                      onChange={(e) => handleSelectOpportunity(e.target.value)} 
                      className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg text-xs font-bold text-slate-200 focus:outline-none focus:border-blue-500"
                    >
                      <option value="" disabled>Select Opportunity...</option>
                      {opportunities.map(o => (
                        <option key={o.id} value={o.id}>{o.title}</option>
                      ))}
                    </select>
                  </div>

                  {/* 3x3 Canvas Grid layout */}
                  {selectedOppDetail && selectedOppDetail.business_model_canvas ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      
                      {/* Customer Segments */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Customer Segments</h4>
                          <span className="text-[8px] bg-green-500/10 border border-green-500/30 text-green-400 px-1.5 py-0.5 rounded font-bold font-mono">EVIDENCE-BACKED</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.customer_segments}</p>
                      </div>

                      {/* Value Propositions */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Value Propositions</h4>
                          <span className="text-[8px] bg-green-500/10 border border-green-500/30 text-green-400 px-1.5 py-0.5 rounded font-bold font-mono">EVIDENCE-BACKED</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.value_propositions}</p>
                      </div>

                      {/* Revenue Streams */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Revenue Model</h4>
                          <span className="text-[8px] bg-purple-500/10 border border-purple-500/30 text-purple-400 px-1.5 py-0.5 rounded font-bold font-mono">AI HYPOTHESIS</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.revenue_streams}</p>
                      </div>

                      {/* Go to Market Channels */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Channels & GTM</h4>
                          <span className="text-[8px] bg-purple-500/10 border border-purple-500/30 text-purple-400 px-1.5 py-0.5 rounded font-bold font-mono">AI HYPOTHESIS</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.channels}</p>
                      </div>

                      {/* Key Activities */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Key Activities</h4>
                          <span className="text-[8px] bg-green-500/10 border border-green-500/30 text-green-400 px-1.5 py-0.5 rounded font-bold font-mono">EVIDENCE-BACKED</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.key_activities}</p>
                      </div>

                      {/* Key Resources */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Key Resources</h4>
                          <span className="text-[8px] bg-green-500/10 border border-green-500/30 text-green-400 px-1.5 py-0.5 rounded font-bold font-mono">EVIDENCE-BACKED</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.key_resources}</p>
                      </div>

                      {/* Cost Structure */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Cost Drivers</h4>
                          <span className="text-[8px] bg-purple-500/10 border border-purple-500/30 text-purple-400 px-1.5 py-0.5 rounded font-bold font-mono">AI HYPOTHESIS</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.cost_structure}</p>
                      </div>

                      {/* First Validation */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">First Validation</h4>
                          <span className="text-[8px] bg-purple-500/10 border border-purple-500/30 text-purple-400 px-1.5 py-0.5 rounded font-bold font-mono">AI HYPOTHESIS</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.first_validation}</p>
                      </div>

                      {/* Potential Partners */}
                      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20 space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Potential Partners</h4>
                          <span className="text-[8px] bg-purple-500/10 border border-purple-500/30 text-purple-400 px-1.5 py-0.5 rounded font-bold font-mono">AI HYPOTHESIS</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{selectedOppDetail.business_model_canvas.key_partners}</p>
                      </div>

                    </div>
                  ) : (
                    <div className="glass-panel p-16 text-center text-slate-500 font-semibold italic">
                      Select an opportunity to display its Canvas blocks.
                    </div>
                  )}

                </div>
              )}

              {/* === HUMAN VALIDATOR TAB === */}
              {activeTab === 'validator' && (
                <div className="space-y-6 max-w-4xl mx-auto">
                  
                  {/* Header info */}
                  <div className="glass-panel p-5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold">Human Validator</h2>
                      <p className="text-slate-450 text-xs mt-0.5">Recalculate metrics, adjust assumptions, and override scores programmatically.</p>
                    </div>
                    
                    <select 
                      value={selectedOppId || ''} 
                      onChange={(e) => handleSelectOpportunity(e.target.value)} 
                      className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg text-xs font-bold text-slate-200 focus:outline-none focus:border-blue-500"
                    >
                      <option value="" disabled>Select Opportunity...</option>
                      {opportunities.map(o => (
                        <option key={o.id} value={o.id}>{o.title}</option>
                      ))}
                    </select>
                  </div>

                  {selectedOppDetail ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      
                      {/* Left Sliders panel */}
                      <div className="md:col-span-2 glass-panel p-6 rounded-xl border border-slate-800 space-y-6 bg-slate-950/20">
                        <h3 className="font-black text-xs uppercase tracking-widest text-slate-405 border-b border-slate-850 pb-2">Adjust Dimensions</h3>
                        
                        {[
                          { label: 'Market Potential', val: valMarket, set: setValMarket },
                          { label: 'Feasibility', val: valFeas, set: setValFeas },
                          { label: 'Strategic Fit', val: valStrat, set: setValStrat },
                          { label: 'Asset Reusability', val: valReuse, set: setValReuse },
                          { label: 'Confidence Score', val: valConf, set: setValConf }
                        ].map((dim, i) => (
                          <div key={i} className="space-y-2">
                            <div className="flex items-center justify-between text-xs font-semibold">
                              <span className="text-slate-300">{dim.label}</span>
                              <span className="font-mono text-cyan-400 font-extrabold">{dim.val} / 100</span>
                            </div>
                            <input 
                              type="range" 
                              min="0" 
                              max="100" 
                              value={dim.val} 
                              onChange={(e) => dim.set(parseInt(e.target.value))}
                              className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-blue-500"
                            />
                          </div>
                        ))}

                        <div className="space-y-1.5 mt-4">
                          <label className="text-[10px] font-bold text-slate-450 block uppercase">Review Notes / Comments</label>
                          <textarea 
                            value={valComments} 
                            onChange={(e) => setValComments(e.target.value)} 
                            className="w-full h-20 bg-slate-900 border border-slate-805 p-3 rounded-lg text-xs focus:outline-none focus:border-blue-500 text-slate-200" 
                            placeholder="State justification details for score overrides..."
                          />
                        </div>
                      </div>

                      {/* Right Recalculation Results panel */}
                      <div className="md:col-span-1 space-y-6">
                        <div className="glass-panel p-6 rounded-xl border border-slate-800 flex flex-col justify-between h-full space-y-6 bg-slate-950/20">
                          <div>
                            <h3 className="font-black text-xs uppercase tracking-widest text-slate-400 border-b border-slate-850 pb-2 mb-5">Score Delta</h3>
                            
                            <div className="flex items-center justify-between bg-slate-900/60 p-4 rounded-xl border border-slate-850/60">
                              <div className="text-center flex-1">
                                <span className="text-[10px] uppercase text-slate-500 font-bold block">Current</span>
                                <span className="text-lg font-extrabold text-slate-400 font-mono">{selectedOppDetail.overall_score}</span>
                              </div>
                              <ArrowRight className="text-slate-600" size={16} />
                              <div className="text-center flex-1">
                                <span className="text-[10px] uppercase text-slate-550 font-bold block">Adjusted</span>
                                <span className="text-2xl font-black text-cyan-400 font-mono">{adjustedScore}</span>
                              </div>
                            </div>

                            <div className="text-center mt-5">
                              <span className={`text-xs font-bold px-3.5 py-1.5 rounded-full border ${
                                adjustedScore - selectedOppDetail.overall_score >= 0 ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-red-500/10 border-red-500/30 text-red-400'
                              }`}>
                                Difference: {adjustedScore - selectedOppDetail.overall_score >= 0 ? '+' : ''}{(adjustedScore - selectedOppDetail.overall_score).toFixed(1)}
                              </span>
                            </div>

                            <p className="text-[11px] text-slate-450 leading-relaxed mt-5 bg-slate-900/30 p-3 rounded-lg border border-slate-855 italic">
                              "{adjustmentExplanation}"
                            </p>
                          </div>

                          <div className="space-y-3">
                            <div>
                              <label className="text-[9px] font-bold text-slate-450 block mb-1.5 uppercase">Workflow State</label>
                              <select 
                                value={valStatus} 
                                onChange={(e) => setValStatus(e.target.value)} 
                                className="w-full bg-slate-900 border border-slate-800 p-2.5 rounded text-xs focus:outline-none focus:border-blue-500 font-semibold"
                              >
                                <option value="pending">PENDING</option>
                                <option value="approved">APPROVED</option>
                                <option value="rejected">REJECTED</option>
                                <option value="under_review">UNDER_REVIEW</option>
                              </select>
                            </div>
                            
                            <button onClick={handleSaveValidation} className="w-full py-3 bg-blue-600 hover:bg-blue-550 text-xs font-bold rounded-xl transition-colors shadow shadow-blue-500/10">
                              Commit Score & Notes
                            </button>
                          </div>
                        </div>
                      </div>

                    </div>
                  ) : (
                    <div className="glass-panel p-16 text-center text-slate-500 font-semibold italic">
                      Select an opportunity to display validation attributes.
                    </div>
                  )}

                </div>
              )}

              {/* === COMPARE MATRIX TAB === */}
              {activeTab === 'compare' && (
                <div className="space-y-6">
                  
                  {/* Selection lists */}
                  <div className="glass-panel p-5 rounded-xl border border-slate-800">
                    <h2 className="text-xl font-black">Venture Matrix Comparison</h2>
                    <p className="text-slate-450 text-xs mt-0.5">Select up to 4 opportunities from the list and compare criteria details side-by-side.</p>
                    
                    <div className="flex flex-wrap gap-2 mt-4">
                      {opportunities.map(opp => {
                        const isSelected = compareIds.includes(opp.id);
                        return (
                          <button 
                            key={opp.id} 
                            onClick={() => toggleCompareSelect(opp.id)}
                            className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-150 ${
                              isSelected ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-900 border-slate-850 text-slate-400 hover:bg-slate-850'
                            }`}
                          >
                            {opp.title}
                          </button>
                        );
                      })}
                      
                      {compareIds.length >= 2 && (
                        <button onClick={handleCompareTrigger} className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-550 text-xs font-bold rounded-xl text-white ml-auto transition-colors">
                          Update Comparison
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Comparisons table */}
                  {compareData.length > 0 ? (
                    <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead>
                            <tr className="border-b border-slate-855 text-slate-400 bg-slate-950/20">
                              <th className="p-4 font-bold uppercase w-44">Metric</th>
                              {compareData.map(opp => (
                                <th key={opp.id} className="p-4 font-extrabold text-sm text-white text-center border-l border-slate-855">{opp.title}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              { label: 'Overall Score', key: 'overall_score', font: 'font-mono text-cyan-400 font-black text-sm' },
                              { label: 'Market Potential', key: 'market_potential', font: 'font-mono' },
                              { label: 'Feasibility', key: 'feasibility', font: 'font-mono' },
                              { label: 'Strategic Fit', key: 'strategic_fit', font: 'font-mono' },
                              { label: 'Asset Reusability', key: 'asset_reusability', font: 'font-mono' },
                              { label: 'Confidence', key: 'confidence', font: 'font-mono' },
                              { label: 'Industry Class', key: 'industry', font: '' },
                              { label: 'Business Model', key: 'business_model', font: '' },
                              { label: 'Revenue Model', key: 'revenue_model', font: '' }
                            ].map((row, idx) => (
                              <tr key={idx} className="border-b border-slate-855 hover:bg-slate-900/10">
                                <td className="p-4 font-bold text-slate-400">{row.label}</td>
                                {compareData.map(opp => (
                                  <td key={opp.id} className={`p-4 text-center border-l border-slate-855 ${row.font}`}>
                                    {opp[row.key as keyof CompareResponse]}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="glass-panel p-16 text-center text-slate-500 font-semibold italic">
                      Select at least 2 opportunities to display comparisons matrices.
                    </div>
                  )}

                </div>
              )}

              {/* === ANALYTICS TAB === */}
              {activeTab === 'analytics' && analytics && (
                <div className="space-y-6">
                  
                  {/* Analytics Stats rows */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="glass-panel p-6 rounded-xl border border-slate-800">
                      <span className="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Asset Reuse Efficiency</span>
                      <span className="text-3xl font-black text-white block mt-1.5 font-mono">{analytics.asset_utilization_rate}%</span>
                      <p className="text-[10px] text-slate-500 mt-1.5">Percentage of uploaded files actively backing opportunities.</p>
                    </div>
                    <div className="glass-panel p-6 rounded-xl border border-slate-800">
                      <span className="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Average Venture Score</span>
                      <span className="text-3xl font-black text-cyan-400 block mt-1.5 font-mono">{analytics.average_overall_score}</span>
                      <p className="text-[10px] text-slate-500 mt-1.5">Mean score across all AI recommendations.</p>
                    </div>
                    <div className="glass-panel p-6 rounded-xl border border-slate-800">
                      <span className="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Knowledge Network Density</span>
                      <span className="text-3xl font-black text-purple-400 block mt-1.5 font-mono">{analytics.total_connections}</span>
                      <p className="text-[10px] text-slate-500 mt-1.5">Total active edge relationships registered in the graph.</p>
                    </div>
                  </div>

                  {/* Charts row */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Score distribution bar chart */}
                    <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-6">Score Distribution Spreads</h3>
                      <div className="w-full h-[240px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={analytics.opportunity_score_distribution}>
                            <XAxis dataKey="range" tick={{ fill: '#64748b', fontSize: 10 }} />
                            <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                            <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Asset types pie chart */}
                    <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-slate-950/20">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-6">Source Document Profiles</h3>
                      <div className="w-full h-[240px] flex items-center justify-center">
                        <div className="w-1/2 h-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie 
                                data={analytics.asset_types_distribution}
                                cx="50%"
                                cy="50%"
                                innerRadius={55}
                                outerRadius={80}
                                dataKey="count"
                                nameKey="name"
                              >
                                {analytics.asset_types_distribution.map((_, index) => (
                                  <Cell key={`cell-${index}`} fill={['#2563eb', '#0891b2', '#7c3aed', '#10b981', '#f59e0b'][index % 5]} />
                                ))}
                              </Pie>
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                        
                        <div className="w-1/2 space-y-2 text-xs">
                          {analytics.asset_types_distribution.map((entry, idx) => (
                            <div key={idx} className="flex items-center space-x-2">
                              <span className="h-3 w-3 rounded-full inline-block" style={{ backgroundColor: ['#2563eb', '#0891b2', '#7c3aed', '#10b981', '#f59e0b'][idx % 5] }}></span>
                              <span className="text-slate-350">{entry.name} ({entry.count})</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* === ARCHITECTURE TAB === */}
              {activeTab === 'architecture' && (
                <div className="space-y-6">
                  {/* Header info */}
                  <div className="glass-panel p-5 rounded-xl border border-slate-800">
                    <h2 className="text-xl font-bold">System Architecture Flow</h2>
                    <p className="text-slate-450 text-xs mt-0.5">Physical layout schematic of the RAG multi-agent processing pipelines.</p>
                  </div>

                  {/* Flow chart diagram blocks */}
                  <div className="glass-panel p-8 rounded-xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden bg-slate-950/20">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl -z-10"></div>
                    
                    {[
                      { num: '01', title: 'Data Ingestion', sub: 'PDF, DOCX, CSV parsing via Docling/Pandas' },
                      { num: '02', title: 'Signal indexing', sub: 'Qdrant Vector DB & SQLite Relationships' },
                      { num: '03', title: 'Retrieval RAG', sub: 'Semantic context matching & citations trace' },
                      { num: '04', title: 'IBM Granite LLM', sub: 'Local multi-agent LangGraph workflow' },
                      { num: '05', title: 'Venture Canvas', sub: 'Recalculated human validation outputs' }
                    ].map((step, idx) => (
                      <React.Fragment key={idx}>
                        <div className="flex-1 bg-slate-900 border border-slate-850 p-6 rounded-2xl space-y-2 text-center min-h-[140px] hover:border-cyan-500/40 transition-colors">
                          <span className="text-xs font-mono font-bold text-cyan-400">STAGE {step.num}</span>
                          <h4 className="font-extrabold text-sm text-white">{step.title}</h4>
                          <p className="text-[10px] text-slate-400 leading-normal">{step.sub}</p>
                        </div>
                        {idx < 4 && (
                          <div className="hidden md:flex flex-col items-center">
                            <ArrowRight className="text-slate-700" size={18} />
                          </div>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}

              {/* === SYSTEM STATUS TAB === */}
              {activeTab === 'system' && (
                <div className="space-y-6">
                  
                  {/* Header info */}
                  <div className="glass-panel p-5 rounded-xl border border-slate-800">
                    <h2 className="text-xl font-bold">System Diagnostics</h2>
                    <p className="text-slate-450 text-xs mt-0.5">Real-time health status checks of all integration database nodes.</p>
                  </div>

                  {/* Diagnostic card grids */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                      { name: 'fastapi', label: 'FastAPI Gateway', desc: 'Main API Gateway Router', info: systemStatus?.fastapi },
                      { name: 'sqlite', label: 'SQLite DB Registry', desc: 'Structured companies & validations database', info: systemStatus?.sqlite },
                      { name: 'ollama', label: 'Ollama Server', desc: 'Local model engine host API', info: systemStatus?.ollama },
                      { name: 'qdrant', label: 'Qdrant Vector DB', desc: 'Semantic vectors index server', info: systemStatus?.qdrant },
                      { name: 'neo4j', label: 'Neo4j Graph Database', desc: 'Knowledge relational connections graph', info: systemStatus?.neo4j },
                      { name: 'langgraph', label: 'LangGraph orchestrator', desc: 'Collaborative agent runner', info: systemStatus?.langgraph }
                    ].map((card, i) => {
                      const statusVal = card.info?.status || 'OFFLINE';
                      
                      return (
                        <div key={i} className="glass-panel p-6 rounded-xl border border-slate-800 flex flex-col justify-between min-h-[160px] bg-slate-950/20">
                          <div>
                            <div className="flex items-center justify-between">
                              <h3 className="font-bold text-sm text-slate-100">{card.label}</h3>
                              <span className={`px-2.5 py-0.5 text-[9px] font-extrabold rounded-full border ${
                                statusVal === 'ONLINE' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
                                statusVal === 'DEGRADED' ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' :
                                'bg-red-500/10 border-red-500/30 text-red-400'
                              }`}>
                                {statusVal}
                              </span>
                            </div>
                            <span className="text-[10px] text-slate-500 mt-1 block font-medium">{card.desc}</span>
                          </div>
                          
                          <p className="text-[11px] text-slate-400 mt-5 leading-normal bg-slate-950/40 p-3 rounded-lg border border-slate-900 font-mono truncate">
                            {card.info?.message || 'Offline fallback mode activated.'}
                          </p>
                        </div>
                      );
                    })}
                  </div>

                  {/* Manual puling setups */}
                  {systemStatus?.ollama.status === 'DEGRADED' && (
                    <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-2xl flex items-start space-x-4 max-w-xl">
                      <AlertTriangle className="text-amber-550 flex-shrink-0 mt-0.5" size={20} />
                      <div className="space-y-2">
                        <span className="font-black text-xs text-amber-500 uppercase block tracking-wider">Granite Model Pulling Guide</span>
                        <p className="text-slate-400 text-xs leading-relaxed">
                          Ollama is online, but model `{systemStatus?.ollama.details?.active_model}` was not detected. Execute this terminal command inside your running Ollama container/host:
                        </p>
                        <code className="block bg-slate-950 p-3.5 rounded-xl border border-slate-900 text-[11px] text-cyan-400 select-all font-mono">
                          ollama pull granite3-dense:8b
                        </code>
                      </div>
                    </div>
                  )}

                </div>
              )}

            </motion.div>
          </AnimatePresence>
        </main>
      </div>

    </div>
  );
}
