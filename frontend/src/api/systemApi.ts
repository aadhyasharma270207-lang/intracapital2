import client from './client';

export interface ServiceStatus {
  status: 'ONLINE' | 'DEGRADED' | 'OFFLINE';
  message?: string;
  details?: Record<string, any>;
}

export interface SystemStatus {
  fastapi: ServiceStatus;
  ollama: ServiceStatus;
  qdrant: ServiceStatus;
  neo4j: ServiceStatus;
  sqlite: ServiceStatus;
  langgraph: ServiceStatus;
}

export const systemApi = {
  getStatus: async (): Promise<SystemStatus> => {
    const response = await client.get('/api/system/status');
    return response.data;
  }
};
export type { ServiceStatus as ApiServiceStatus };
