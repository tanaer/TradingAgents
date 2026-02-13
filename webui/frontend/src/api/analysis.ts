import apiClient from './client'
import type { AnalysisRequest, AnalysisStatus, AnalysisReport } from '@/types'

export const analysisApi = {
  start: (request: AnalysisRequest) =>
    apiClient.post<any, { task_id: string; message: string }>('/analysis/start', request),

  getStatus: (taskId: string) => apiClient.get<any, AnalysisStatus>(`/analysis/status/${taskId}`),

  getReport: (taskId: string) => apiClient.get<any, AnalysisReport>(`/analysis/report/${taskId}`),

  list: (limit: number = 20) => apiClient.get<any, any[]>('/analysis/list', { params: { limit } }),

  cancel: (taskId: string) => apiClient.delete<any, { message: string }>(`/analysis/${taskId}`),

  getStreamUrl: (taskId: string) => `/api/analysis/stream/${taskId}`,
}
