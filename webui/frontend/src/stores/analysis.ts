import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analysisApi, WebSocketClient } from '@/api'
import type { AnalysisRequest, AnalysisStatus, AnalysisReport, WSMessage } from '@/types'
import { ElMessage } from 'element-plus'

export const useAnalysisStore = defineStore('analysis', () => {
  const currentTaskId = ref<string | null>(null)
  const status = ref<AnalysisStatus | null>(null)
  const report = ref<AnalysisReport | null>(null)
  const wsClient = ref<WebSocketClient | null>(null)
  const loading = ref(false)

  const isRunning = computed(() => status.value?.status === 'running')
  const isCompleted = computed(() => status.value?.status === 'completed')
  const isFailed = computed(() => status.value?.status === 'failed')
  const progress = computed(() => status.value?.progress || 0)

  async function startAnalysis(request: AnalysisRequest) {
    loading.value = true
    try {
      const result = await analysisApi.start(request)
      currentTaskId.value = result.task_id

      // Initialize status
      status.value = {
        task_id: result.task_id,
        status: 'pending',
        progress: 0,
        agents: request.analysts.map((a) => ({
          name: a,
          status: 'pending',
          progress: 0,
          message: null,
        })),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      // Connect WebSocket for real-time updates
      connectWebSocket(result.task_id)

      ElMessage.success('Analysis started')
      return result.task_id
    } catch (error) {
      ElMessage.error(`Failed to start analysis: ${(error as Error).message}`)
      return null
    } finally {
      loading.value = false
    }
  }

  function connectWebSocket(taskId: string) {
    // Close existing connection
    if (wsClient.value) {
      wsClient.value.close()
    }

    wsClient.value = new WebSocketClient(taskId)

    // Handle all messages
    wsClient.value.on('*', (message: WSMessage) => {
      handleWSMessage(message)
    })

    wsClient.value.connect().catch((error) => {
      console.error('WebSocket connection failed:', error)
      // Fall back to polling
      startPolling(taskId)
    })
  }

  function handleWSMessage(message: WSMessage) {
    switch (message.type) {
      case 'status':
        status.value = {
          task_id: message.task_id,
          status: (message as any).status,
          progress: (message as any).progress,
          agents: (message as any).agents,
          created_at: status.value?.created_at || message.timestamp,
          updated_at: message.timestamp,
        }
        break

      case 'report':
        report.value = {
          task_id: message.task_id,
          ticker: (message as any).ticker,
          market: (message as any).market,
          analysis_date: new Date().toISOString().split('T')[0],
          report: (message as any).report,
          created_at: message.timestamp,
        }
        break

      case 'completed':
        if ((message as any).success) {
          ElMessage.success('Analysis completed')
        } else {
          ElMessage.error((message as any).message || 'Analysis failed')
        }
        break

      case 'error':
        ElMessage.error((message as any).message || 'An error occurred')
        break
    }
  }

  let pollingInterval: ReturnType<typeof setInterval> | null = null

  function startPolling(taskId: string) {
    if (pollingInterval) {
      clearInterval(pollingInterval)
    }

    pollingInterval = setInterval(async () => {
      try {
        const newStatus = await analysisApi.getStatus(taskId)
        status.value = newStatus

        if (newStatus.status === 'completed') {
          const reportData = await analysisApi.getReport(taskId)
          report.value = reportData
          stopPolling()
        } else if (newStatus.status === 'failed') {
          stopPolling()
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }, 2000)
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  async function fetchStatus(taskId: string) {
    try {
      status.value = await analysisApi.getStatus(taskId)
    } catch (error) {
      ElMessage.error(`Failed to fetch status: ${(error as Error).message}`)
    }
  }

  async function fetchReport(taskId: string) {
    try {
      report.value = await analysisApi.getReport(taskId)
    } catch (error) {
      ElMessage.error(`Failed to fetch report: ${(error as Error).message}`)
    }
  }

  async function cancelAnalysis() {
    if (!currentTaskId.value) return

    try {
      await analysisApi.cancel(currentTaskId.value)
      if (wsClient.value) {
        wsClient.value.close()
        wsClient.value = null
      }
      stopPolling()
      ElMessage.info('Analysis cancelled')
    } catch (error) {
      ElMessage.error(`Failed to cancel: ${(error as Error).message}`)
    }
  }

  function reset() {
    currentTaskId.value = null
    status.value = null
    report.value = null
    if (wsClient.value) {
      wsClient.value.close()
      wsClient.value = null
    }
    stopPolling()
  }

  return {
    currentTaskId,
    status,
    report,
    loading,
    isRunning,
    isCompleted,
    isFailed,
    progress,
    startAnalysis,
    fetchStatus,
    fetchReport,
    cancelAnalysis,
    reset,
  }
})
