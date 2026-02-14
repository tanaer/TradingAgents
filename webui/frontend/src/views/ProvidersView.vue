<template>
  <div class="providers-view">
    <el-page-header @back="$router.back()">
      <template #content>
        <span class="page-title">LLM Providers</span>
      </template>
      <template #extra>
        <el-button type="primary" @click="showCreateCustom = true">
          <el-icon><Plus /></el-icon>
          Add Custom Provider
        </el-button>
      </template>
    </el-page-header>

    <el-alert
      type="info"
      title="Configure your LLM providers"
      description="Set up API keys for the LLM providers you want to use for analysis. You can add custom models to any provider."
      :closable="false"
      show-icon
      style="margin: 20px 0"
    />

    <el-tabs v-model="activeTab">
      <el-tab-pane label="Built-in Providers" name="builtin">
        <el-row :gutter="20">
          <el-col :span="12" v-for="provider in builtInProviders" :key="provider.id">
            <ProviderCard
              :provider="provider"
              @configure="handleConfigure"
              @test="handleTest"
              @addModel="handleAddModel"
              @removeModel="handleRemoveModel"
            />
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="Custom Providers" name="custom">
        <el-row :gutter="20">
          <el-col :span="12" v-for="provider in customProviders" :key="provider.id">
            <ProviderCard
              :provider="provider"
              @configure="handleConfigureCustom"
              @test="handleTest"
              @copy="handleCopy"
              @delete="handleDelete"
              @addModel="handleAddModel"
              @removeModel="handleRemoveModel"
            />
          </el-col>
        </el-row>
        <el-empty v-if="customProviders.length === 0" description="No custom providers yet">
          <el-button type="primary" @click="showCreateCustom = true">
            Create Custom Provider
          </el-button>
        </el-empty>
      </el-tab-pane>
    </el-tabs>

    <!-- Configuration Dialog -->
    <ProviderConfigDialog
      v-model="configDialogVisible"
      :provider="selectedProvider"
      @saved="handleConfigSaved"
    />

    <!-- Create Custom Provider Dialog -->
    <CreateCustomProviderDialog
      v-model="showCreateCustom"
      @created="handleCustomCreated"
    />

    <!-- Copy Provider Dialog -->
    <el-dialog v-model="copyDialogVisible" title="Copy Provider" width="400px">
      <el-form label-width="100px">
        <el-form-item label="New Name">
          <el-input v-model="copyNewName" placeholder="Enter name for the copy" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleCopyConfirm" :disabled="!copyNewName.trim()">
          Copy
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProviderStore } from '@/stores'
import { ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import ProviderCard from '@/components/providers/ProviderCard.vue'
import ProviderConfigDialog from '@/components/providers/ProviderConfigDialog.vue'
import CreateCustomProviderDialog from '@/components/providers/CreateCustomProviderDialog.vue'
import type { ProviderInfo, CustomProviderInstance } from '@/types'

const providerStore = useProviderStore()

const activeTab = ref('builtin')
const configDialogVisible = ref(false)
const showCreateCustom = ref(false)
const selectedProvider = ref<ProviderInfo | null>(null)
const copyDialogVisible = ref(false)
const copyNewName = ref('')
const copySourceProvider = ref<ProviderInfo | null>(null)

const builtInProviders = computed(() =>
  providerStore.providers.filter((p) => !p.id.startsWith('custom:'))
)

const customProviders = computed(() =>
  providerStore.providers.filter((p) => p.id.startsWith('custom:'))
)

function handleConfigure(provider: ProviderInfo) {
  selectedProvider.value = provider
  configDialogVisible.value = true
}

function handleConfigureCustom(provider: ProviderInfo) {
  // For custom providers, we might want a different dialog
  // For now, use the same dialog
  selectedProvider.value = provider
  configDialogVisible.value = true
}

async function handleTest(provider: ProviderInfo) {
  if (provider.models.length > 0) {
    await providerStore.testProvider(provider.id, provider.models[0])
  }
}

async function handleAddModel(providerId: string, modelName: string) {
  await providerStore.addModel(providerId, modelName)
}

async function handleRemoveModel(providerId: string, modelName: string) {
  await providerStore.removeModel(providerId, modelName)
}

function handleCopy(provider: ProviderInfo) {
  copySourceProvider.value = provider
  copyNewName.value = `${provider.name} (Copy)`
  copyDialogVisible.value = true
}

async function handleCopyConfirm() {
  if (!copySourceProvider.value || !copyNewName.value.trim()) return

  const instanceId = copySourceProvider.value.id.replace('custom:', '')
  await providerStore.copyCustomProvider(instanceId, copyNewName.value.trim())
  copyDialogVisible.value = false
  copySourceProvider.value = null
  copyNewName.value = ''
}

async function handleDelete(provider: ProviderInfo) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${provider.name}"?`,
      'Delete Provider',
      { type: 'warning' }
    )
    const instanceId = provider.id.replace('custom:', '')
    await providerStore.deleteCustomProvider(instanceId)
  } catch {
    // User cancelled
  }
}

function handleConfigSaved() {
  providerStore.fetchProviders()
}

function handleCustomCreated(instance: CustomProviderInstance) {
  console.log('Custom provider created:', instance)
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
