import { defineStore } from 'pinia'
import { ref } from 'vue'
import { marketsApi } from '@/api'
import type { MarketInfo, StockSearchResult, PopularStock, MarketType } from '@/types'
import { ElMessage } from 'element-plus'

export const useMarketStore = defineStore('market', () => {
  const markets = ref<MarketInfo[]>([])
  const selectedMarket = ref<MarketType>('us')
  const searchResults = ref<StockSearchResult[]>([])
  const popularStocks = ref<PopularStock[]>([])
  const loading = ref(false)

  async function fetchMarkets() {
    try {
      markets.value = await marketsApi.list()
    } catch (error) {
      ElMessage.error(`Failed to fetch markets: ${(error as Error).message}`)
    }
  }

  async function searchStocks(query: string, market?: string) {
    if (!query.trim()) {
      searchResults.value = []
      return
    }

    loading.value = true
    try {
      searchResults.value = await marketsApi.search(
        query,
        market || selectedMarket.value,
        10
      )
    } catch (error) {
      ElMessage.error(`Search failed: ${(error as Error).message}`)
    } finally {
      loading.value = false
    }
  }

  async function fetchPopularStocks(market?: string) {
    const targetMarket = market || selectedMarket.value
    try {
      popularStocks.value = await marketsApi.getPopular(targetMarket)
    } catch (error) {
      ElMessage.error(`Failed to fetch popular stocks: ${(error as Error).message}`)
    }
  }

  function setMarket(market: MarketType) {
    selectedMarket.value = market
    fetchPopularStocks(market)
  }

  return {
    markets,
    selectedMarket,
    searchResults,
    popularStocks,
    loading,
    fetchMarkets,
    searchStocks,
    fetchPopularStocks,
    setMarket,
  }
})
