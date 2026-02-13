<template>
  <el-card class="progress-tracker">
    <template #header>
      <div class="tracker-header">
        <span>Analysis Progress</span>
        <el-tag :type="statusType">{{ statusText }}</el-tag>
      </div>
    </template>

    <!-- Overall Progress -->
    <div class="overall-progress">
      <el-progress
        :percentage="Math.round(progress * 100)"
        :status="progressStatus"
        :stroke-width="20"
      />
    </div>

    <!-- Agent Status Grid -->
    <div class="agents-grid">
      <div
        v-for="agent in agents"
        :key="agent.name"
        class="agent-card"
        :class="`status-${agent.status}`"
      >
        <div class="agent-header">
          <el-icon :size="20">
            <component :is="getAgentIcon(agent.name)" />
          </el-icon>
          <span class="agent-name">{{ formatAgentName(agent.name) }}</span>
        </div>
        <el-progress
          :percentage="Math.round(agent.progress * 100)"
          :status="getAgentProgressStatus(agent.status)"
          :stroke-width="6"
        />
        <div class="agent-message" v-if="agent.message">
          {{ agent.message }}
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="tracker-actions" v-if="isRunning">
      <el-button type="danger" @click="$emit('cancel')">
        Cancel Analysis
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  TrendCharts,
  ChatDotRound,
  Document,
  DataLine,
} from '@element-plus/icons-vue'
import type { AgentStatus, AnalysisStatusType } from '@/types'

const props = defineProps<{
  status: AnalysisStatusType
  progress: number
  agents: AgentStatus[]
}>()

const emit = defineEmits<{
  cancel: []
}>()

const statusType = computed(() => {
  switch (props.status) {
    case 'completed':
      return 'success'
    case 'running':
      return 'primary'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
})

const statusText = computed(() => {
  switch (props.status) {
    case 'completed':
      return 'Completed'
    case 'running':
      return 'Running'
    case 'failed':
      return 'Failed'
    default:
      return 'Pending'
  }
})

const progressStatus = computed(() => {
  if (props.status === 'completed') return 'success'
  if (props.status === 'failed') return 'exception'
  return undefined
})

const isRunning = computed(() => props.status === 'running')

function getAgentIcon(name: string) {
  switch (name) {
    case 'market':
      return TrendCharts
    case 'social':
      return ChatDotRound
    case 'news':
      return Document
    case 'fundamentals':
      return DataLine
    default:
      return Document
  }
}

function formatAgentName(name: string) {
  return name.charAt(0).toUpperCase() + name.slice(1) + ' Analyst'
}

function getAgentProgressStatus(status: string) {
  switch (status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'exception'
    default:
      return undefined
  }
}
</script>

<style scoped>
.progress-tracker {
  margin-bottom: 20px;
}

.tracker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overall-progress {
  margin-bottom: 20px;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.agent-card {
  padding: 12px;
  border-radius: 8px;
  background: #f5f7fa;
  border-left: 3px solid #c0c4cc;
}

.agent-card.status-running {
  border-left-color: #409eff;
  background: #ecf5ff;
}

.agent-card.status-completed {
  border-left-color: #67c23a;
  background: #f0f9eb;
}

.agent-card.status-failed {
  border-left-color: #f56c6c;
  background: #fef0f0;
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.agent-name {
  font-weight: 500;
}

.agent-message {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.tracker-actions {
  margin-top: 16px;
  text-align: center;
}
</style>
