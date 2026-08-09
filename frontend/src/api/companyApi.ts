import client from './client';

export interface Company {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export const companyApi = {
  create: async (name: string, description?: string): Promise<Company> => {
    const response = await client.post('/api/company', { name, description });
    return response.data;
  },
  get: async (id: string): Promise<Company> => {
    const response = await client.get(`/api/company/${id}`);
    return response.data;
  }
};
