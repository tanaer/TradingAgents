// Provider types
export interface ProviderInfo {
  id: string
  name: string
  base_url: string | null
  models: string[]
  is_configured: boolean
}

export interface ProviderConfig {
  provider_id: string
  api_key: string
  base_url?: string
}

export interface ProviderTestRequest {
  provider_id: string
  model: string
}

export interface ProviderTestResponse {
  success: boolean
  message: string
  latency_ms?: number
}

// Analysis types
export type MarketType = 'us' | 'hk' | 'cn'
export type AnalystType = 'market' | 'social' | 'news' | 'fundamentals'
export type AnalysisStatusType = 'pending' | 'running' | 'completed' | 'failed'

export interface AnalysisRequest {
  ticker: string
  market: MarketType
  analysts: AnalystType[]
  analysis_date?: string
  research_depth: number
  llm_provider: string
  shallow_model: string
  deep_model: string
}

export interface AgentStatus {
  name: string
  status: string
  progress: number
  message: string | null
}

export interface AnalysisStatus {
  task_id: string
  status: AnalysisStatusType
  progress: number
  agents: AgentStatus[]
  created_at: string
  updated_at: string
}

export interface AnalysisReport {
  task_id: string
  ticker: string
  market: MarketType
  analysis_date: string
  report: string
  created_at: string
}

// Market types
export interface MarketInfo {
  id: string
  name: string
  data_source: string
  symbol_format: string
  description: string
}

export interface StockSearchResult {
  symbol: string
  name: string
  market: string
  exchange?: string
}

export interface PopularStock {
  symbol: string
  name: string
  market: string
  price?: number
  change_percent?: number
}

// WebSocket message types
export interface WSMessage {
  type: string
  task_id: string
  timestamp: string
  [key: string]: unknown
}

export interface WSStatusMessage extends WSMessage {
  type: 'status'
  status: AnalysisStatusType
  progress: number
  agents: AgentStatus[]
}

export interface WSReportMessage extends WSMessage {
  type: 'report'
  ticker: string
  market: string
  report: string
}

export interface WSEventMessage extends WSMessage {
  type: 'agent_status' | 'report_chunk' | 'completed' | 'error'
  [key: string]: unknown
}
