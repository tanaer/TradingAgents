import apiClient from './client'
import type {
  ProviderInfo,
  ProviderWithCustomModels,
  ProviderConfig,
  ProviderTestRequest,
  ProviderTestResponse,
  CustomProviderInstance,
  CreateCustomProviderRequest,
  UpdateCustomProviderRequest,
  CopyProviderConfigRequest,
  AddModelRequest,
} from '@/types'

export const providersApi = {
  // Built-in providers
  list: () => apiClient.get<any, ProviderInfo[]>('/providers'),

  get: (providerId: string) =>
    apiClient.get<any, ProviderWithCustomModels>(`/providers/${providerId}`),

  configure: (config: ProviderConfig) =>
    apiClient.post('/providers/configure', config),

  test: (request: ProviderTestRequest) =>
    apiClient.post<any, ProviderTestResponse>('/providers/test', request),

  // Model management
  addModel: (providerId: string, modelName: string) =>
    apiClient.post<any, { success: boolean; message: string }>(
      `/providers/${encodeURIComponent(providerId)}/models`,
      { model_name: modelName } as AddModelRequest
    ),

  removeModel: (providerId: string, modelName: string) =>
    apiClient.delete<any, { success: boolean; message: string }>(
      `/providers/${encodeURIComponent(providerId)}/models/${encodeURIComponent(modelName)}`
    ),

  // Custom provider instances
  createCustom: (request: CreateCustomProviderRequest) =>
    apiClient.post<any, CustomProviderInstance>('/providers/custom', request),

  listCustom: () =>
    apiClient.get<any, CustomProviderInstance[]>('/providers/custom/list'),

  getCustom: (instanceId: string) =>
    apiClient.get<any, CustomProviderInstance>(`/providers/custom/${instanceId}`),

  updateCustom: (instanceId: string, request: UpdateCustomProviderRequest) =>
    apiClient.put<any, CustomProviderInstance>(`/providers/custom/${instanceId}`, request),

  deleteCustom: (instanceId: string) =>
    apiClient.delete<any, { message: string }>(`/providers/custom/${instanceId}`),

  copyCustom: (instanceId: string, newName: string) =>
    apiClient.post<any, CustomProviderInstance>(
      `/providers/custom/${instanceId}/copy`,
      { source_instance_id: instanceId, new_name: newName } as CopyProviderConfigRequest
    ),
}
