import apiClient from './client'
import type { ProviderInfo, ProviderConfig, ProviderTestRequest, ProviderTestResponse } from '@/types'

export const providersApi = {
  list: () => apiClient.get<any, ProviderInfo[]>('/providers'),

  get: (providerId: string) => apiClient.get<any, ProviderInfo>(`/providers/${providerId}`),

  configure: (config: ProviderConfig) => apiClient.post('/providers/configure', config),

  test: (request: ProviderTestRequest) =>
    apiClient.post<any, ProviderTestResponse>('/providers/test', request),
}
