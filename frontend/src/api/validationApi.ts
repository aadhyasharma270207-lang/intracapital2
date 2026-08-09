import client from './client';
import type { ValidationResponse } from './opportunityApi';

export interface ValidationRequest {
  market_potential: number;
  feasibility: number;
  strategic_fit: number;
  asset_reusability: number;
  confidence: number;
  comments?: string;
  status?: string;
}

export const validationApi = {
  validate: async (opportunityId: string, data: ValidationRequest): Promise<ValidationResponse> => {
    const response = await client.post(`/api/opportunities/${opportunityId}/validate`, data);
    return response.data;
  }
};
