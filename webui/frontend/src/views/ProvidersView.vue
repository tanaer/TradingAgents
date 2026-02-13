<template>
  <div class="providers-view">
    <el-page-header @back="$router.back()">
      <template #content>
        <span class="page-title">LLM Providers</span>
      </template>
    </el-page-header>

    <el-alert
      type="info"
      title="Configure your LLM providers"
      description="Set up API keys for the LLM providers you want to use for analysis."
      :closable="false"
      show-icon
      style="margin: 20px 0"
    />

    <el-row :gutter="20">
      <el-col :span="12" v-for="provider in providers" :key="provider.id">
        <ProviderCard
          :provider="provider"
          @configure="handleConfigure"
          @test="handleTest"
        />
      </el-col>
    </el-row>

    <!-- Configuration Dialog -->
    <ProviderConfigDialog
      v-model="configDialogVisible"
      :provider="selectedProvider"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProviderStore } from '@/stores'
import ProviderCard from '@/components/providers/ProviderCard.vue'
import ProviderConfigDialog from '@/components/providers/ProviderConfigDialog.vue'
import type { ProviderInfo } from '@/types'

const providerStore = useProviderStore()

const providers = computed(() => providerStore.providers)
const configDialogVisible = ref(false)
const selectedProvider = ref<ProviderInfo | null>(null)

function handleConfigure(provider: ProviderInfo) {
  selectedProvider.value = provider
  configDialogVisible.value = true
}

async function handleTest(provider: ProviderInfo) {
  if (provider.models.length > 0) {
    await providerStore.testProvider(provider.id, provider.models[0])
  }
}

onMounted(() => {
  providerStore.fetchProviders()
})
</script>

<style scoped>
.providers-view {
  padding: 0;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
}
</style>
