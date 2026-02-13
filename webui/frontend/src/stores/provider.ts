import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { providersApi } from '@/api'
import type { ProviderInfo, ProviderConfig, ProviderTestResponse } from '@/types'
import { ElMessage } from 'element-plus'

export const useProviderStore = defineStore('provider', () => {
  const providers = ref<ProviderInfo[]>([])
  const loading = ref(false)
  const selectedProvider = ref<string | null>(null)

  const configuredProviders = computed(() =>
    providers.value.filter((p) => p.is_configured)
  )

  const unconfiguredProviders = computed(() =>
    providers.value.filter((p) => !p.is_configured)
  )

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

  async function configureProvider(config: ProviderConfig) {
    try {
      await providersApi.configure(config)
      await fetchProviders() // Refresh the list
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

  function getProviderById(id: string): ProviderInfo | undefined {
    return providers.value.find((p) => p.id === id)
  }

  return {
    providers,
    loading,
    selectedProvider,
    configuredProviders,
    unconfiguredProviders,
    fetchProviders,
    configureProvider,
    testProvider,
    getProviderById,
  }
})
