import client from './client';

export interface Asset {
  id: string;
  company_id: string;
  file_name: string;
  asset_type: string;
  department?: string;
  source?: string;
  created_at: string;
  status: string;
  metadata_json?: Record<string, any>;
  relationships_count?: number;
  chunks_count?: number;
}

export interface AssetDetail extends Asset {
  content?: string;
}

export const assetApi = {
  upload: async (companyId: string, file: File, department?: string, source?: string): Promise<Asset> => {
    const formData = new FormData();
    formData.append('company_id', companyId);
    formData.append('file', file);
    if (department) formData.append('department', department);
    if (source) formData.append('source', source);

    const response = await client.post('/api/assets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  list: async (companyId?: string): Promise<Asset[]> => {
    const response = await client.get('/api/assets', {
      params: companyId ? { company_id: companyId } : {},
    });
    return response.data;
  },
  get: async (id: string): Promise<AssetDetail> => {
    const response = await client.get(`/api/assets/${id}`);
    return response.data;
  },
  delete: async (id: string): Promise<{ status: string; message: string }> => {
    const response = await client.delete(`/api/assets/${id}`);
    return response.data;
  }
};
