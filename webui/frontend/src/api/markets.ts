import apiClient from './client'
import type { MarketInfo, StockSearchResult, PopularStock } from '@/types'

export const marketsApi = {
  list: () => apiClient.get<any, MarketInfo[]>('/markets'),

  search: (query: string, market?: string, limit: number = 10) =>
    apiClient.get<any, StockSearchResult[]>('/markets/search', {
      params: { query, market, limit },
    }),

  getPopular: (market: string) =>
    apiClient.get<any, PopularStock[]>(`/markets/${market}/popular`),
}
