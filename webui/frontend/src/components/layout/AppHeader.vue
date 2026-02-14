<template>
  <div class="header">
    <div class="left">
      <!-- Mobile menu button -->
      <el-button
        class="menu-btn"
        :icon="Menu"
        @click="$emit('toggle-sidebar')"
      />
      <div class="logo">
        <el-icon size="20"><TrendCharts /></el-icon>
        <span class="title">TradingAgents</span>
      </div>
    </div>
    <div class="actions">
      <el-button type="primary" size="small" @click="$router.push('/analysis')">
        <el-icon><Plus /></el-icon>
        <span class="btn-text">New</span>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Menu } from '@element-plus/icons-vue'

defineEmits<{
  'toggle-sidebar': []
}>()
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu-btn {
  display: none;
  background: transparent;
  border: none;
  color: white;
  padding: 5px;
}

.menu-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 10px;
}

/* Mobile styles */
@media (max-width: 768px) {
  .menu-btn {
    display: flex;
  }

  .logo {
    gap: 6px;
  }

  .title {
    font-size: 16px;
  }

  .btn-text {
    display: none;
  }

  .actions .el-button {
    padding: 8px 12px;
  }
}

@media (max-width: 480px) {
  .title {
    font-size: 14px;
  }
}
</style>
