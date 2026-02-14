<template>
  <el-form :model="form" label-width="120px" class="analysis-form" label-position="top">
    <el-collapse v-model="activeCollapse">
      <!-- Basic Settings -->
      <el-collapse-item title="Basic Settings" name="basic">
        <!-- Market Selection -->
        <el-form-item label="Market">
          <el-radio-group v-model="form.market" class="market-radio">
            <el-radio-button label="us">US</el-radio-button>
            <el-radio-button label="hk">HK</el-radio-button>
            <el-radio-button label="cn">A-Share</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- Ticker Input with Search -->
        <el-form-item label="Stock Ticker">
          <el-autocomplete
            v-model="form.ticker"
            :fetch-suggestions="searchStocks"
            placeholder="Search or enter ticker"
            @select="handleStockSelect"
            style="width: 100%"
            :loading="searchLoading"
          >
            <template #default="{ item }">
              <div class="stock-suggestion">
                <span class="symbol">{{ item.symbol }}</span>
                <span class="name">{{ item.name }}</span>
                <el-tag size="small" type="info">{{ item.market.toUpperCase() }}</el-tag>
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
          <el-checkbox-group v-model="form.analysts" class="analyst-checkbox">
            <el-checkbox v-for="analyst in availableAnalysts" :key="analyst.id" :label="analyst.id">
              {{ analyst.name }}
            </el-checkbox>
          </el-checkbox-group>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            Select multiple analysts for comprehensive analysis
          </div>
        </el-form-item>
      </el-collapse-item>

      <!-- Research Depth Settings -->
      <el-collapse-item title="Research Depth" name="depth">
        <el-form-item label="Depth Preset">
          <el-radio-group v-model="depthPreset" @change="applyDepthPreset" class="depth-radio">
            <el-radio-button label="shallow">Shallow</el-radio-button>
            <el-radio-button label="medium">Medium</el-radio-button>
            <el-radio-button label="deep">Deep</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Debate Rounds">
          <el-slider v-model="form.max_debate_rounds" :min="1" :max="10" show-input />
          <div class="form-tip">Bull/Bear researchers debate rounds</div>
        </el-form-item>

        <el-form-item label="Risk Discussion">
          <el-slider v-model="form.max_risk_discuss_rounds" :min="1" :max="10" show-input />
          <div class="form-tip">Risk debators discussion rounds</div>
        </el-form-item>

        <!-- Agent Swarm Toggles -->
        <el-form-item label="Bull/Bear Debate">
          <div class="switch-row">
            <el-switch v-model="form.enable_bull_bear_debate" />
            <span class="switch-label">Enable researcher debate</span>
          </div>
        </el-form-item>

        <el-form-item label="Risk Analysis">
          <div class="switch-row">
            <el-switch v-model="form.enable_risk_analysis" />
            <span class="switch-label">Enable risk debators</span>
          </div>
        </el-form-item>
      </el-collapse-item>

      <!-- LLM Configuration -->
      <el-collapse-item title="LLM Configuration" name="llm">
        <el-form-item label="LLM Provider">
          <el-select v-model="form.llm_provider" placeholder="Select provider" @change="handleProviderChange" style="width: 100%">
            <el-option-group label="Configured Providers">
              <el-option
                v-for="provider in configuredProviders"
                :key="provider.id"
                :label="provider.name"
                :value="provider.id"
              />
            </el-option-group>
          </el-select>
        </el-form-item>

        <el-form-item label="Quick Model">
          <el-select v-model="form.shallow_model" placeholder="Select quick thinking model" filterable allow-create style="width: 100%">
            <el-option
              v-for="model in availableModels"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Deep Model">
          <el-select v-model="form.deep_model" placeholder="Select deep thinking model" filterable allow-create style="width: 100%">
            <el-option
              v-for="model in availableModels"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Temperature">
          <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
      </el-collapse-item>

      <!-- Advanced Settings -->
      <el-collapse-item title="Advanced Settings" name="advanced">
        <el-form-item label="Data Vendor">
          <el-select v-model="form.data_vendor" style="width: 100%">
            <el-option label="Yahoo Finance" value="yfinance" />
            <el-option label="Alpha Vantage" value="alpha_vantage" />
          </el-select>
        </el-form-item>

        <el-form-item label="OpenAI Reasoning" v-if="form.llm_provider === 'openai'">
          <el-select v-model="form.openai_reasoning_effort" clearable style="width: 100%">
            <el-option label="Low" value="low" />
            <el-option label="Medium" value="medium" />
            <el-option label="High" value="high" />
          </el-select>
        </el-form-item>

        <el-form-item label="Google Thinking" v-if="form.llm_provider === 'google'">
          <el-select v-model="form.google_thinking_level" clearable style="width: 100%">
            <el-option label="Minimal" value="minimal" />
            <el-option label="High" value="high" />
          </el-select>
        </el-form-item>
      </el-collapse-item>
    </el-collapse>

    <!-- Agent Swarm Info -->
    <el-alert
      type="info"
      :closable="false"
      class="swarm-alert"
    >
      <template #title>
        <strong>Agent Swarm Architecture</strong>
      </template>
      <div class="swarm-info">
        <p>1. <strong>Analysts</strong>: Gather and analyze market data</p>
        <p>2. <strong>Bull/Bear Researchers</strong>: Debate from different perspectives</p>
        <p>3. <strong>Research Manager</strong>: Synthesizes insights</p>
        <p>4. <strong>Trader</strong>: Makes recommendations</p>
        <p>5. <strong>Risk Debators</strong>: Evaluate risk levels</p>
      </div>
    </el-alert>

    <el-form-item class="submit-btn">
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!isFormValid"
        @click="handleSubmit"
        style="width: 100%"
      >
        <el-icon><CaretRight /></el-icon>
        Start Analysis
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProviderStore, useMarketStore } from '@/stores'
import { marketsApi } from '@/api'
import { InfoFilled, CaretRight } from '@element-plus/icons-vue'
import type { AnalysisRequest, MarketType, AnalystType, StockSearchResult } from '@/types'

const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [request: AnalysisRequest]
}>()

const providerStore = useProviderStore()
const marketStore = useMarketStore()

const activeCollapse = ref(['basic', 'depth'])
const depthPreset = ref('medium')
const searchLoading = ref(false)

const form = ref({
  ticker: '',
  market: 'us' as MarketType,
  analysis_date: '',
  analysts: ['market', 'fundamentals'] as AnalystType[],
  max_debate_rounds: 3,
  max_risk_discuss_rounds: 2,
  llm_provider: '',
  shallow_model: '',
  deep_model: '',
  temperature: 0.7,
  openai_reasoning_effort: '' as string | null,
  google_thinking_level: '' as string | null,
  data_vendor: 'yfinance',
  enable_bull_bear_debate: true,
  enable_risk_analysis: true,
})

const availableAnalysts = [
  { id: 'market', name: 'Market', description: 'Technical analysis' },
  { id: 'social', name: 'Social Media', description: 'Sentiment analysis' },
  { id: 'news', name: 'News', description: 'News impact' },
  { id: 'fundamentals', name: 'Fundamentals', description: 'Financial metrics' },
]

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

const depthPresets = {
  shallow: { debate_rounds: 1, risk_rounds: 1 },
  medium: { debate_rounds: 3, risk_rounds: 2 },
  deep: { debate_rounds: 5, risk_rounds: 3 },
}

function applyDepthPreset(preset: string) {
  const config = depthPresets[preset as keyof typeof depthPresets]
  if (config) {
    form.value.max_debate_rounds = config.debate_rounds
    form.value.max_risk_discuss_rounds = config.risk_rounds
  }
}

// Watch for manual changes to update preset
watch([() => form.value.max_debate_rounds, () => form.value.max_risk_discuss_rounds], ([debate, risk]) => {
  if (debate === 1 && risk === 1) depthPreset.value = 'shallow'
  else if (debate === 3 && risk === 2) depthPreset.value = 'medium'
  else if (debate === 5 && risk === 3) depthPreset.value = 'deep'
  else depthPreset.value = ''
})

// Update models when provider changes
function handleProviderChange(providerId: string) {
  const provider = providerStore.getProviderById(providerId)
  if (provider && provider.models.length > 0) {
    form.value.shallow_model = provider.models[0]
    form.value.deep_model = provider.models[0]
  }
}

async function searchStocks(query: string, cb: (results: StockSearchResult[]) => void) {
  if (!query.trim()) {
    cb([])
    return
  }

  searchLoading.value = true
  try {
    const results = await marketsApi.search(query, form.value.market, 20)
    cb(results)
  } catch (error) {
    console.error('Search failed:', error)
    cb([])
  } finally {
    searchLoading.value = false
  }
}

function handleStockSelect(item: StockSearchResult) {
  form.value.ticker = item.symbol
  // Auto-detect market from symbol
  if (item.symbol.endsWith('.HK')) {
    form.value.market = 'hk'
  } else if (item.symbol.endsWith('.SH') || item.symbol.endsWith('.SZ')) {
    form.value.market = 'cn'
  } else {
    form.value.market = 'us'
  }
}

function handleSubmit() {
  emit('submit', {
    ticker: form.value.ticker.toUpperCase(),
    market: form.value.market,
    analysis_date: form.value.analysis_date || undefined,
    analysts: form.value.analysts,
    max_debate_rounds: form.value.max_debate_rounds,
    max_risk_discuss_rounds: form.value.max_risk_discuss_rounds,
    llm_provider: form.value.llm_provider,
    shallow_model: form.value.shallow_model,
    deep_model: form.value.deep_model,
    temperature: form.value.temperature > 0 ? form.value.temperature : undefined,
    openai_reasoning_effort: form.value.openai_reasoning_effort || undefined,
    google_thinking_level: form.value.google_thinking_level || undefined,
    data_vendor: form.value.data_vendor,
    enable_bull_bear_debate: form.value.enable_bull_bear_debate,
    enable_risk_analysis: form.value.enable_risk_analysis,
  } as AnalysisRequest)
}

// Initialize
onMounted(() => {
  providerStore.fetchProviders()
  marketStore.fetchMarkets()
})
</script>

<style scoped>
.analysis-form {
  max-width: 700px;
}

.stock-suggestion {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stock-suggestion .symbol {
  font-weight: bold;
  min-width: 80px;
}

.stock-suggestion .name {
  color: #606266;
  flex: 1;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.switch-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.switch-label {
  color: #606266;
}

.swarm-alert {
  margin: 16px 0;
}

.swarm-info {
  font-size: 13px;
  line-height: 1.6;
}

.swarm-info p {
  margin: 4px 0;
}

.submit-btn {
  margin-top: 16px;
}

:deep(.el-collapse-item__header) {
  font-weight: bold;
  font-size: 14px;
}

:deep(.el-slider__runway.show-input) {
  margin-right: 80px;
}

:deep(.el-form-item__label) {
  padding-bottom: 4px;
}

/* Mobile styles */
@media (max-width: 768px) {
  .analysis-form {
    max-width: 100%;
  }

  .stock-suggestion {
    flex-wrap: wrap;
    gap: 6px;
  }

  .stock-suggestion .symbol {
    min-width: auto;
  }

  .stock-suggestion .name {
    width: 100%;
    font-size: 12px;
  }

  .market-radio,
  .depth-radio {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .market-radio .el-radio-button,
  .depth-radio .el-radio-button {
    flex: 1;
    min-width: 80px;
  }

  .analyst-checkbox {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .swarm-info {
    font-size: 12px;
  }

  :deep(.el-slider__runway.show-input) {
    margin-right: 70px;
  }

  :deep(.el-slider__input) {
    width: 60px;
  }

  .switch-label {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  :deep(.el-collapse-item__header) {
    font-size: 13px;
    padding: 0 10px;
  }

  :deep(.el-collapse-item__content) {
    padding: 10px;
  }

  .form-tip {
    font-size: 11px;
  }
}
</style>
