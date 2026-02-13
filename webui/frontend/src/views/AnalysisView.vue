<template>
  <div class="analysis-view">
    <el-row :gutter="20">
      <!-- Analysis Form -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <span>New Analysis</span>
          </template>
          <AnalysisForm
            :loading="analysisStore.loading"
            @submit="handleSubmit"
          />
        </el-card>
      </el-col>

      <!-- Progress & Results -->
      <el-col :span="14">
        <!-- Progress Tracker -->
        <ProgressTracker
          v-if="analysisStore.status"
          :status="analysisStore.status.status"
          :progress="analysisStore.progress"
          :agents="analysisStore.status.agents"
          @cancel="handleCancel"
        />

        <!-- Report Viewer -->
        <ReportViewer
          v-if="analysisStore.report"
          :report="analysisStore.report"
        />

        <!-- Empty State -->
        <el-card v-if="!analysisStore.status && !analysisStore.report">
          <el-empty description="Start an analysis to see results here" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalysisStore, useProviderStore, useMarketStore } from '@/stores'
import AnalysisForm from '@/components/analysis/AnalysisForm.vue'
import ProgressTracker from '@/components/analysis/ProgressTracker.vue'
import ReportViewer from '@/components/analysis/ReportViewer.vue'
import type { AnalysisRequest } from '@/types'

const route = useRoute()
const analysisStore = useAnalysisStore()
const providerStore = useProviderStore()
const marketStore = useMarketStore()

async function handleSubmit(request: AnalysisRequest) {
  await analysisStore.startAnalysis(request)
}

async function handleCancel() {
  await analysisStore.cancelAnalysis()
}

onMounted(() => {
  providerStore.fetchProviders()
  marketStore.fetchMarkets()

  // Check for query params (from home page quick analyze)
  if (route.query.ticker) {
    // The form will pick this up
  }

  // Reset analysis state when leaving
  return () => {
    if (analysisStore.isCompleted || analysisStore.isFailed) {
      analysisStore.reset()
    }
  }
})

onUnmounted(() => {
  // Clean up WebSocket connection
  analysisStore.reset()
})
</script>

<style scoped>
.analysis-view {
  padding: 0;
}
</style>
