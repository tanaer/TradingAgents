<template>
  <el-card class="provider-card" :class="{ configured: provider.is_configured }">
    <template #header>
      <div class="card-header">
        <span class="provider-name">{{ provider.name }}</span>
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

    <div class="provider-actions">
      <el-button size="small" @click="$emit('configure', provider)">
        {{ provider.is_configured ? 'Reconfigure' : 'Configure' }}
      </el-button>
      <el-button
        size="small"
        type="primary"
        :disabled="!provider.is_configured"
        @click="$emit('test', provider)"
      >
        Test Connection
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { ProviderInfo } from '@/types'

defineProps<{
  provider: ProviderInfo
}>()

defineEmits<{
  configure: [provider: ProviderInfo]
  test: [provider: ProviderInfo]
}>()
</script>

<style scoped>
.provider-card {
  margin-bottom: 16px;
}

.provider-card.configured {
  border-left: 3px solid #67c23a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.provider-actions {
  display: flex;
  gap: 8px;
}
</style>
