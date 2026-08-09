import client from './client';

export interface CategoryCount {
  name: string;
  count: number;
}

export interface ScoreDistribution {
  range: string;
  count: number;
}

export interface AnalyticsData {
  total_assets: number;
  processed_assets: number;
  failed_assets: number;
  total_opportunities: number;
  average_overall_score: number;
  average_confidence: number;
  asset_types_distribution: CategoryCount[];
  industry_distribution: CategoryCount[];
  opportunity_score_distribution: ScoreDistribution[];
  asset_utilization_rate: number;
  total_connections: number;
}

export const analyticsApi = {
  get: async (): Promise<AnalyticsData> => {
    const response = await client.get('/api/analytics');
    return response.data;
  }
};
