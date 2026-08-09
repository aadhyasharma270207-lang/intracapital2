import client from './client';
import type { ProcessingJob } from './processingApi';

export const discoveryApi = {
  start: async (companyId: string): Promise<ProcessingJob> => {
    const response = await client.post('/api/discovery/start', null, {
      params: { company_id: companyId }
    });
    return response.data;
  },
  getStatus: async (jobId: string): Promise<ProcessingJob> => {
    const response = await client.get(`/api/discovery/${jobId}`);
    return response.data;
  }
};
