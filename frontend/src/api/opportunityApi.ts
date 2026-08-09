import client from './client';
import type { OpportunityEvidenceResponse } from './evidenceApi';

export interface Opportunity {
  id: string;
  company_id: string;
  title: string;
  short_description: string;
  overall_score: number;
  market_potential: number;
  feasibility: number;
  strategic_fit: number;
  asset_reusability: number;
  confidence: number;
  industry: string;
  status: string;
  created_at: string;
}

export interface BusinessModelCanvas {
  id: string;
  opportunity_id: string;
  customer_segments: string;
  value_propositions: string;
  channels: string;
  customer_relationships: string;
  revenue_streams: string;
  key_resources: string;
  key_activities: string;
  key_partners: string;
  cost_structure: string;
  first_validation: string;
}

export interface ValidationResponse {
  id: string;
  opportunity_id: string;
  market_potential: number;
  feasibility: number;
  strategic_fit: number;
  asset_reusability: number;
  confidence: number;
  overall_score: number;
  adjusted_by: string;
  comments?: string;
  status: string;
  created_at: string;
}

export interface OpportunityDetail extends Opportunity {
  problem: string;
  solution: string;
  target_customers: string;
  business_model: string;
  revenue_model: string;
  required_resources?: string;
  existing_assets_used?: string;
  key_activities?: string;
  key_resources?: string;
  cost_drivers?: string;
  go_to_market?: string;
  risks?: string;
  assumptions?: string;
  reasoning?: string;
  evidence: OpportunityEvidenceResponse[];
  business_model_canvas?: BusinessModelCanvas;
  validation_results: ValidationResponse[];
}

export interface CompareResponse {
  id: string;
  title: string;
  overall_score: number;
  market_potential: number;
  feasibility: number;
  strategic_fit: number;
  asset_reusability: number;
  confidence: number;
  short_description: string;
  industry: string;
  business_model: string;
  revenue_model: string;
  required_resources?: string;
  risks?: string;
}

export const opportunityApi = {
  list: async (
    companyId?: string, 
    sortBy?: string, 
    order?: 'asc' | 'desc', 
    minScore?: number, 
    industry?: string, 
    status?: string
  ): Promise<Opportunity[]> => {
    const response = await client.get('/api/opportunities', {
      params: {
        company_id: companyId,
        sort_by: sortBy,
        order,
        min_score: minScore,
        industry,
        status
      }
    });
    return response.data;
  },
  get: async (id: string): Promise<OpportunityDetail> => {
    const response = await client.get(`/api/opportunities/${id}`);
    return response.data;
  },
  compare: async (ids: string[]): Promise<CompareResponse[]> => {
    const response = await client.post('/api/opportunities/compare', {
      opportunity_ids: ids
    });
    return response.data;
  },
  approve: async (id: string): Promise<Opportunity> => {
    const response = await client.post(`/api/opportunities/${id}/approve`);
    return response.data;
  },
  reject: async (id: string): Promise<Opportunity> => {
    const response = await client.post(`/api/opportunities/${id}/reject`);
    return response.data;
  }
};
