import client from './client';
import type { ProcessingJob } from './processingApi';

export const demoApi = {
  load: async (): Promise<ProcessingJob> => {
    const response = await client.post('/api/demo/load');
    return response.data;
  }
};
