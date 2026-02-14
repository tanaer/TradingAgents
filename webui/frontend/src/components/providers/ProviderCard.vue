<template>
  <el-card class="provider-card" :class="{ configured: provider.is_configured, custom: isCustom }">
    <template #header>
      <div class="card-header">
        <div class="title-section">
          <span class="provider-name">{{ provider.name }}</span>
          <el-tag v-if="isCustom" type="warning" size="small">Custom</el-tag>
        </div>
        <el-tag :type="provider.is_configured ? 'success' : 'info'" size="small">
          {{ provider.is_configured ? 'Configured' : 'Not Configured' }}
        </el-tag>
      </div>
    </template>

    <div class="provider-info">
      <div class="info-row">
        <span class="label">ID:</span>
        <span class="value">{{ provider.id }}</span>
      </div>
      <div class="info-row" v-if="provider.base_url">
        <span class="label">Base URL:</span>
        <span class="value url">{{ provider.base_url }}</span>
      </div>
      <div class="info-row">
        <span class="label">Models:</span>
        <span class="value">{{ provider.models.length }} available</span>
      </div>
    </div>

    <!-- Models List with Add/Remove -->
    <div class="models-section">
      <div class="models-header">
        <span>Models</span>
        <el-button size="small" @click="showAddModel = true">
          <el-icon><Plus /></el-icon>
          Add Model
        </el-button>
      </div>
      <div class="models-list">
        <el-tag
          v-for="model in displayModels"
          :key="model"
          closable
          @close="handleRemoveModel(model)"
          class="model-tag"
        >
          {{ model }}
        </el-tag>
        <el-button
          v-if="provider.models.length > maxDisplayModels"
          link
          size="small"
          @click="showAllModels = !showAllModels"
        >
          {{ showAllModels ? 'Show less' : `+${provider.models.length - maxDisplayModels} more` }}
        </el-button>
      </div>
    </div>

    <!-- Add Model Dialog -->
    <el-dialog v-model="showAddModel" title="Add Custom Model" width="400px">
      <el-input
        v-model="newModelName"
        placeholder="Enter model name (e.g., gpt-4o, claude-3-opus)"
        @keyup.enter="handleAddModel"
      />
      <template #footer>
        <el-button @click="showAddModel = false">Cancel</el-button>
        <el-button type="primary" @click="handleAddModel" :disabled="!newModelName.trim()">
          Add Model
        </el-button>
      </template>
    </el-dialog>

    <div class="provider-actions">
      <el-button size="small" @click="$emit('configure', provider)">
        {{ provider.is_configured ? 'Edit' : 'Configure' }}
      </el-button>
      <el-button
        size="small"
        type="primary"
        :disabled="!provider.is_configured"
        @click="$emit('test', provider)"
      >
        Test
      </el-button>
      <el-button
        v-if="isCustom"
        size="small"
        @click="$emit('copy', provider)"
      >
        <el-icon><CopyDocument /></el-icon>
        Copy
      </el-button>
      <el-button
        v-if="isCustom"
        size="small"
        type="danger"
        @click="$emit('delete', provider)"
      >
        <el-icon><Delete /></el-icon>
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, CopyDocument, Delete } from '@element-plus/icons-vue'
import type { ProviderInfo } from '@/types'

const props = defineProps<{
  provider: ProviderInfo
}>()

const emit = defineEmits<{
  configure: [provider: ProviderInfo]
  test: [provider: ProviderInfo]
  copy: [provider: ProviderInfo]
  delete: [provider: ProviderInfo]
  addModel: [providerId: string, modelName: string]
  removeModel: [providerId: string, modelName: string]
}>()

const isCustom = computed(() => props.provider.id.startsWith('custom:'))
const maxDisplayModels = 5
const showAllModels = ref(false)
const showAddModel = ref(false)
const newModelName = ref('')

const displayModels = computed(() => {
  if (showAllModels.value || props.provider.models.length <= maxDisplayModels) {
    return props.provider.models
  }
  return props.provider.models.slice(0, maxDisplayModels)
})

function handleAddModel() {
  if (newModelName.value.trim()) {
    emit('addModel', props.provider.id, newModelName.value.trim())
    newModelName.value = ''
    showAddModel.value = false
  }
}

function handleRemoveModel(model: string) {
  emit('removeModel', props.provider.id, model)
}
</script>

<style scoped>
.provider-card {
  margin-bottom: 16px;
}

.provider-card.configured {
  border-left: 3px solid #67c23a;
}

.provider-card.custom {
  border-left: 3px solid #e6a23c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.provider-name {
  font-weight: bold;
  font-size: 16px;
}

.provider-info {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.value {
  color: #303133;
}

.value.url {
  font-size: 12px;
  word-break: break-all;
}

.models-section {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.models-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 500;
}

.models-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.model-tag {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.provider-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Mobile styles */
@media (max-width: 768px) {
  .provider-name {
    font-size: 14px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .info-row {
    flex-direction: column;
    gap: 2px;
  }

  .label {
    width: auto;
  }

  .models-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .models-section {
    padding: 10px;
  }

  .model-tag {
    max-width: 120px;
    font-size: 12px;
  }

  .provider-actions {
    flex-direction: column;
  }

  .provider-actions .el-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .provider-card :deep(.el-card__body) {
    padding: 12px;
  }

  .provider-card :deep(.el-card__header) {
    padding: 12px;
  }

  .model-tag {
    max-width: 100px;
  }
}
</style>
