<template>
  <el-card class="report-viewer">
    <template #header>
      <div class="viewer-header">
        <span>Analysis Report</span>
        <div class="header-actions">
          <el-button size="small" @click="copyReport">
            <el-icon><CopyDocument /></el-icon>
            Copy
          </el-button>
          <el-button size="small" @click="downloadReport">
            <el-icon><Download /></el-icon>
            Download
          </el-button>
        </div>
      </div>
    </template>

    <div class="report-meta">
      <el-tag>{{ report.ticker }}</el-tag>
      <el-tag type="info">{{ report.market.toUpperCase() }}</el-tag>
      <el-tag type="warning">{{ report.analysis_date }}</el-tag>
    </div>

    <el-divider />

    <div class="report-content" v-html="renderedReport"></div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'
import type { AnalysisReport } from '@/types'

const props = defineProps<{
  report: AnalysisReport
}>()

const renderedReport = computed(() => {
  return marked(props.report.report)
})

function copyReport() {
  navigator.clipboard.writeText(props.report.report)
  ElMessage.success('Report copied to clipboard')
}

function downloadReport() {
  const blob = new Blob([props.report.report], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analysis-${props.report.ticker}-${props.report.analysis_date}.md`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Report downloaded')
}
</script>

<style scoped>
.report-viewer {
  margin-top: 20px;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.report-meta {
  display: flex;
  gap: 8px;
}

.report-content {
  line-height: 1.8;
}

.report-content :deep(h1) {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.report-content :deep(h2) {
  margin-top: 30px;
  margin-bottom: 15px;
  color: #303133;
}

.report-content :deep(h3) {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #606266;
}

.report-content :deep(ul) {
  padding-left: 20px;
}

.report-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.report-content :deep(pre) {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
}
</style>
