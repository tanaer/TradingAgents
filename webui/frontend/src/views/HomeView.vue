<template>
  <div class="home-view">
    <el-row :gutter="20">
      <!-- Quick Stats -->
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Total Analyses" :value="stats.total">
            <template #prefix>
              <el-icon><DataAnalysis /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Completed" :value="stats.completed">
            <template #prefix>
              <el-icon><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Providers" :value="stats.providers">
            <template #prefix>
              <el-icon><Setting /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Markets" :value="3">
            <template #prefix>
              <el-icon><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- Quick Start -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Quick Start</span>
          </template>
          <el-steps :active="quickStartStep" finish-status="success">
            <el-step title="Configure Provider" />
            <el-step title="Select Stock" />
            <el-step title="Run Analysis" />
          </el-steps>
          <div style="margin-top: 20px; text-align: center">
            <el-button type="primary" size="large" @click="$router.push('/analysis')">
              Start New Analysis
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- Popular Stocks -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Popular Stocks</span>
              <el-select v-model="selectedMarket" size="small" style="width: 100px">
                <el-option label="US" value="us" />
                <el-option label="HK" value="hk" />
                <el-option label="CN" value="cn" />
              </el-select>
            </div>
          </template>
          <el-table :data="popularStocks" style="width: 100%">
            <el-table-column prop="symbol" label="Symbol" width="100" />
            <el-table-column prop="name" label="Name" />
            <el-table-column label="Action" width="80">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  link
                  @click="analyzeStock(row.symbol)"
                >
                  Analyze
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProviderStore, useMarketStore } from '@/stores'

const router = useRouter()
const providerStore = useProviderStore()
const marketStore = useMarketStore()

const selectedMarket = ref('us')

const stats = computed(() => ({
  total: 0,
  completed: 0,
  providers: providerStore.configuredProviders.length,
}))

const quickStartStep = computed(() => {
  if (providerStore.configuredProviders.length === 0) return 0
  return 1
})

const popularStocks = computed(() => marketStore.popularStocks)

function analyzeStock(symbol: string) {
  router.push({ path: '/analysis', query: { ticker: symbol, market: selectedMarket.value } })
}

watch(selectedMarket, (market) => {
  marketStore.fetchPopularStocks(market)
})

onMounted(() => {
  providerStore.fetchProviders()
  marketStore.fetchPopularStocks(selectedMarket.value)
})
</script>

<style scoped>
.home-view {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
