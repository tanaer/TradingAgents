<template>
  <el-form :model="form" label-width="120px" class="analysis-form">
    <!-- Market Selection -->
    <el-form-item label="Market">
      <el-radio-group v-model="form.market">
        <el-radio-button label="us">US</el-radio-button>
        <el-radio-button label="hk">HK</el-radio-button>
        <el-radio-button label="cn">A-Share</el-radio-button>
      </el-radio-group>
    </el-form-item>

    <!-- Ticker Input -->
    <el-form-item label="Stock Ticker">
      <el-autocomplete
        v-model="form.ticker"
        :fetch-suggestions="searchStocks"
        placeholder="Search or enter ticker"
        @select="handleStockSelect"
        style="width: 100%"
      >
        <template #default="{ item }">
          <div class="stock-suggestion">
            <span class="symbol">{{ item.symbol }}</span>
            <span class="name">{{ item.name }}</span>
          </div>
        </template>
      </el-autocomplete>
    </el-form-item>

    <!-- Analysis Date -->
    <el-form-item label="Analysis Date">
      <el-date-picker
        v-model="form.analysis_date"
        type="date"
        placeholder="Select date (default: today)"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        style="width: 100%"
      />
    </el-form-item>

    <!-- Analyst Selection -->
    <el-form-item label="Analysts">
      <el-checkbox-group v-model="form.analysts">
        <el-checkbox label="market">Market</el-checkbox>
        <el-checkbox label="social">Social</el-checkbox>
        <el-checkbox label="news">News</el-checkbox>
        <el-checkbox label="fundamentals">Fundamentals</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <!-- Research Depth -->
    <el-form-item label="Research Depth">
      <el-slider v-model="form.research_depth" :min="1" :max="5" :step="1" show-stops />
    </el-form-item>

    <el-divider>LLM Configuration</el-divider>

    <!-- Provider Selection -->
    <el-form-item label="LLM Provider">
      <el-select v-model="form.llm_provider" placeholder="Select provider">
        <el-option
          v-for="provider in configuredProviders"
          :key="provider.id"
          :label="provider.name"
          :value="provider.id"
        />
      </el-select>
    </el-form-item>

    <!-- Model Selection -->
    <el-form-item label="Quick Model">
      <el-select v-model="form.shallow_model" placeholder="Select quick thinking model">
        <el-option
          v-for="model in availableModels"
          :key="model"
          :label="model"
          :value="model"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="Deep Model">
      <el-select v-model="form.deep_model" placeholder="Select deep thinking model">
        <el-option
          v-for="model in availableModels"
          :key="model"
          :label="model"
          :value="model"
        />
      </el-select>
    </el-form-item>

    <el-form-item>
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!isFormValid"
        @click="handleSubmit"
      >
        Start Analysis
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useProviderStore, useMarketStore } from '@/stores'
import type { AnalysisRequest, MarketType, AnalystType, StockSearchResult } from '@/types'

const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [request: AnalysisRequest]
}>()

const providerStore = useProviderStore()
const marketStore = useMarketStore()

const form = ref({
  ticker: '',
  market: 'us' as MarketType,
  analysis_date: '',
  analysts: ['market', 'fundamentals'] as AnalystType[],
  research_depth: 3,
  llm_provider: '',
  shallow_model: '',
  deep_model: '',
})

const configuredProviders = computed(() => providerStore.configuredProviders)

const availableModels = computed(() => {
  const provider = providerStore.getProviderById(form.value.llm_provider)
  return provider?.models || []
})

const isFormValid = computed(() => {
  return (
    form.value.ticker &&
    form.value.analysts.length > 0 &&
    form.value.llm_provider &&
    form.value.shallow_model &&
    form.value.deep_model
  )
})

// Update models when provider changes
watch(() => form.value.llm_provider, (providerId) => {
  const provider = providerStore.getProviderById(providerId)
  if (provider && provider.models.length > 0) {
    form.value.shallow_model = provider.models[0]
    form.value.deep_model = provider.models[0]
  }
})

async function searchStocks(query: string, cb: (results: StockSearchResult[]) => void) {
  await marketStore.searchStocks(query, form.value.market)
  cb(marketStore.searchResults)
}

function handleStockSelect(item: StockSearchResult) {
  form.value.ticker = item.symbol
}

function handleSubmit() {
  emit('submit', {
    ticker: form.value.ticker.toUpperCase(),
    market: form.value.market,
    analysis_date: form.value.analysis_date || undefined,
    analysts: form.value.analysts,
    research_depth: form.value.research_depth,
    llm_provider: form.value.llm_provider,
    shallow_model: form.value.shallow_model,
    deep_model: form.value.deep_model,
  })
}

// Initialize
providerStore.fetchProviders()
</script>

<style scoped>
.analysis-form {
  max-width: 600px;
}

.stock-suggestion {
  display: flex;
  justify-content: space-between;
}

.stock-suggestion .symbol {
  font-weight: bold;
}

.stock-suggestion .name {
  color: #909399;
  font-size: 12px;
}
</style>
