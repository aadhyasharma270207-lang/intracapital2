import client from './client';

export interface OpportunityEvidenceResponse {
  id: string;
  opportunity_id: string;
  chunk_id: string;
  asset_id: string;
  file_name: string;
  asset_type: string;
  relevance_score: number;
  supporting_text: string;
}

export const evidenceApi = {
  get: async (opportunityId: string): Promise<OpportunityEvidenceResponse[]> => {
    const response = await client.get(`/api/opportunities/${opportunityId}/evidence`);
    return response.data;
  }
};
