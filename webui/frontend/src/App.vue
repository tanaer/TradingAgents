<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <el-header>
          <AppHeader @toggle-sidebar="toggleSidebar" />
        </el-header>
        <el-container>
          <!-- Desktop Sidebar -->
          <el-aside width="200px" class="desktop-sidebar">
            <AppSidebar />
          </el-aside>
          <!-- Mobile Drawer -->
          <el-drawer
            v-model="sidebarVisible"
            direction="ltr"
            :size="200"
            :with-header="false"
            class="mobile-drawer"
          >
            <AppSidebar @select="closeSidebar" />
          </el-drawer>
          <el-main>
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'

const sidebarVisible = ref(false)

function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
}

function closeSidebar() {
  sidebarVisible.value = false
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-container {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 15px;
  height: 50px !important;
}

.el-aside {
  background-color: #304156;
  color: white;
}

.el-main {
  background-color: #f0f2f5;
  padding: 15px;
  overflow-y: auto;
}

/* Desktop: show sidebar, hide drawer */
.desktop-sidebar {
  display: block;
}

.mobile-drawer {
  display: none;
}

/* Mobile styles */
@media (max-width: 768px) {
  .el-header {
    padding: 0 10px;
    height: 50px !important;
  }

  .el-main {
    padding: 10px;
  }

  /* Hide desktop sidebar on mobile */
  .desktop-sidebar {
    display: none;
  }
}

/* Drawer styles */
:deep(.el-drawer__body) {
  padding: 0;
  background-color: #304156;
}

:deep(.el-overlay) {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
