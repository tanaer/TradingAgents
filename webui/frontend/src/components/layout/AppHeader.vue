<template>
  <div class="header">
    <div class="logo">
      <el-icon size="24"><TrendCharts /></el-icon>
      <span class="title">TradingAgents</span>
    </div>
    <div class="actions">
      <el-button type="primary" @click="$router.push('/analysis')">
        <el-icon><Plus /></el-icon>
        New Analysis
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title {
  font-size: 20px;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>
