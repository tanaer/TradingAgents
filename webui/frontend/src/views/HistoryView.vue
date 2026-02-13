<template>
  <div class="history-view">
    <el-page-header @back="$router.back()">
      <template #content>
        <span class="page-title">Analysis History</span>
      </template>
    </el-page-header>

    <el-card style="margin-top: 20px">
      <el-table :data="analyses" style="width: 100%">
        <el-table-column prop="task_id" label="Task ID" width="300">
          <template #default="{ row }">
            <el-text truncated>{{ row.task_id }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="Progress" width="150">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.progress * 100)"
              :status="row.status === 'completed' ? 'success' : undefined"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Created" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed'"
              type="primary"
              link
              @click="viewReport(row.task_id)"
            >
              View Report
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { analysisApi } from '@/api'

const router = useRouter()

interface AnalysisListItem {
  task_id: string
  status: string
  progress: number
  created_at: string
}

const analyses = ref<AnalysisListItem[]>([])

function getStatusType(status: string) {
  switch (status) {
    case 'completed':
      return 'success'
    case 'running':
      return 'primary'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString()
}

function viewReport(taskId: string) {
  // In a real app, you'd navigate to a report view or open a modal
  router.push({ path: '/analysis', query: { taskId } })
}

onMounted(async () => {
  try {
    analyses.value = await analysisApi.list(50)
  } catch (error) {
    console.error('Failed to fetch analysis history:', error)
  }
})
</script>

<style scoped>
.history-view {
  padding: 0;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
}
</style>
