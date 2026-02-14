import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { providersApi } from '@/api'
import type {
  ProviderInfo,
  ProviderConfig,
  ProviderTestResponse,
  CustomProviderInstance,
  CreateCustomProviderRequest,
  UpdateCustomProviderRequest,
} from '@/types'
import { ElMessage } from 'element-plus'

export const useProviderStore = defineStore('provider', () => {
  const providers = ref<ProviderInfo[]>([])
  const customProviders = ref<CustomProviderInstance[]>([])
  const loading = ref(false)
  const selectedProvider = ref<string | null>(null)

  const configuredProviders = computed(() =>
    providers.value.filter((p) => p.is_configured)
  )

  const unconfiguredProviders = computed(() =>
    providers.value.filter((p) => !p.is_configured)
  )

  const allProviders = computed(() => {
    // Merge built-in and custom providers
    return providers.value
  })

  async function fetchProviders() {
    loading.value = true
    try {
      providers.value = await providersApi.list()
    } catch (error) {
      ElMessage.error(`Failed to fetch providers: ${(error as Error).message}`)
    } finally {
      loading.value = false
    }
  }

  async function fetchCustomProviders() {
    try {
      customProviders.value = await providersApi.listCustom()
    } catch (error) {
      console.error('Failed to fetch custom providers:', error)
    }
  }

  async function configureProvider(config: ProviderConfig) {
    try {
      await providersApi.configure(config)
      await fetchProviders()
      ElMessage.success(`Provider ${config.provider_id} configured successfully`)
      return true
    } catch (error) {
      ElMessage.error(`Failed to configure provider: ${(error as Error).message}`)
      return false
    }
  }

  async function testProvider(providerId: string, model: string): Promise<ProviderTestResponse> {
    try {
      const result = await providersApi.test({
        provider_id: providerId,
        model,
      })
      if (result.success) {
        ElMessage.success(`Connection successful (${result.latency_ms}ms)`)
      } else {
        ElMessage.error(`Connection failed: ${result.message}`)
      }
      return result
    } catch (error) {
      const response: ProviderTestResponse = {
        success: false,
        message: (error as Error).message,
      }
      ElMessage.error(`Test failed: ${response.message}`)
      return response
    }
  }

  async function addModel(providerId: string, modelName: string) {
    try {
      await providersApi.addModel(providerId, modelName)
      await fetchProviders()
      ElMessage.success(`Model '${modelName}' added`)
      return true
    } catch (error) {
      ElMessage.error(`Failed to add model: ${(error as Error).message}`)
      return false
    }
  }

  async function removeModel(providerId: string, modelName: string) {
    try {
      await providersApi.removeModel(providerId, modelName)
      await fetchProviders()
      ElMessage.success(`Model '${modelName}' removed`)
      return true
    } catch (error) {
      ElMessage.error(`Failed to remove model: ${(error as Error).message}`)
      return false
    }
  }

  // Custom provider management
  async function createCustomProvider(request: CreateCustomProviderRequest) {
    try {
      const instance = await providersApi.createCustom(request)
      await fetchProviders()
      ElMessage.success(`Custom provider '${request.name}' created`)
      return instance
    } catch (error) {
      ElMessage.error(`Failed to create provider: ${(error as Error).message}`)
      return null
    }
  }

  async function updateCustomProvider(instanceId: string, request: UpdateCustomProviderRequest) {
    try {
      const instance = await providersApi.updateCustom(instanceId, request)
      await fetchProviders()
      ElMessage.success('Provider updated')
      return instance
    } catch (error) {
      ElMessage.error(`Failed to update provider: ${(error as Error).message}`)
      return null
    }
  }

  async function deleteCustomProvider(instanceId: string) {
    try {
      await providersApi.deleteCustom(instanceId)
      await fetchProviders()
      ElMessage.success('Provider deleted')
      return true
    } catch (error) {
      ElMessage.error(`Failed to delete provider: ${(error as Error).message}`)
      return false
    }
  }

  async function copyCustomProvider(instanceId: string, newName: string) {
    try {
      const instance = await providersApi.copyCustom(instanceId, newName)
      await fetchProviders()
      ElMessage.success(`Provider copied as '${newName}'`)
      return instance
    } catch (error) {
      ElMessage.error(`Failed to copy provider: ${(error as Error).message}`)
      return null
    }
  }

  function getProviderById(id: string): ProviderInfo | undefined {
    return providers.value.find((p) => p.id === id)
  }

  return {
    providers,
    customProviders,
    loading,
    selectedProvider,
    configuredProviders,
    unconfiguredProviders,
    allProviders,
    fetchProviders,
    fetchCustomProviders,
    configureProvider,
    testProvider,
    addModel,
    removeModel,
    createCustomProvider,
    updateCustomProvider,
    deleteCustomProvider,
    copyCustomProvider,
    getProviderById,
  }
})
