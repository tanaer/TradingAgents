<template>
  <el-menu
    :default-active="activeMenu"
    class="sidebar-menu"
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409EFF"
    router
    @select="handleSelect"
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>Dashboard</span>
    </el-menu-item>

    <el-menu-item index="/analysis">
      <el-icon><DataAnalysis /></el-icon>
      <span>Analysis</span>
    </el-menu-item>

    <el-menu-item index="/providers">
      <el-icon><Setting /></el-icon>
      <span>Providers</span>
    </el-menu-item>

    <el-menu-item index="/history">
      <el-icon><Clock /></el-icon>
      <span>History</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const emit = defineEmits<{
  select: []
}>()

const route = useRoute()
const activeMenu = computed(() => route.path)

function handleSelect() {
  emit('select')
}
</script>

<style scoped>
.sidebar-menu {
  border-right: none;
  height: 100%;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}

.el-menu-item:hover {
  background-color: #263445 !important;
}

.el-menu-item.is-active {
  background-color: #263445 !important;
}

/* Mobile: larger touch targets */
@media (max-width: 768px) {
  .el-menu-item {
    height: 56px;
    line-height: 56px;
  }
}
</style>
