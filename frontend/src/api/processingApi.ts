import client from './client';

export interface ProcessingJob {
  id: string;
  company_id: string;
  job_type: string;
  status: string;
  current_step?: string;
  progress: number;
  elapsed_time: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export const processingApi = {
  getStatus: async (jobId: string): Promise<ProcessingJob> => {
    const response = await client.get(`/api/processing/${jobId}`);
    return response.data;
  }
};
