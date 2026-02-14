<template>
  <el-dialog
    v-model="visible"
    title="Create Custom Provider"
    width="500px"
  >
    <el-form :model="form" label-width="100px">
      <el-form-item label="Name" required>
        <el-input v-model="form.name" placeholder="My OpenAI Compatible API" />
      </el-form-item>

      <el-form-item label="Provider Type">
        <el-select v-model="form.provider_type" placeholder="Select provider type">
          <el-option label="OpenAI Compatible (NewAPI)" value="newapi" />
          <el-option label="OpenAI" value="openai" />
          <el-option label="Ollama" value="ollama" />
        </el-select>
      </el-form-item>

      <el-form-item label="Base URL" required>
        <el-input v-model="form.base_url" placeholder="https://api.example.com/v1" />
      </el-form-item>

      <el-form-item label="API Key" required>
        <el-input
          v-model="form.api_key"
          type="password"
          show-password
          placeholder="Enter your API key"
        />
      </el-form-item>

      <el-form-item label="Initial Models">
        <el-select
          v-model="form.models"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="Enter or select models"
        >
          <el-option
            v-for="model in commonModels"
            :key="model"
            :label="model"
            :value="model"
          />
        </el-select>
        <div class="form-tip">Type and press Enter to add custom models</div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">Cancel</el-button>
      <el-button type="primary" @click="handleCreate" :loading="creating" :disabled="!isFormValid">
        Create Provider
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useProviderStore } from '@/stores'
import { ElMessage } from 'element-plus'
import type { CustomProviderInstance, CreateCustomProviderRequest } from '@/types'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'created': [instance: CustomProviderInstance]
}>()

const providerStore = useProviderStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const creating = ref(false)

const form = ref<CreateCustomProviderRequest>({
  name: '',
  provider_type: 'newapi',
  base_url: '',
  api_key: '',
  models: [],
})

const commonModels = [
  'gpt-4o',
  'gpt-4o-mini',
  'gpt-4-turbo',
  'gpt-3.5-turbo',
  'claude-3-opus',
  'claude-3-sonnet',
  'claude-3-haiku',
  'llama-3-70b',
  'llama-3-8b',
  'qwen-72b-chat',
  'qwen-7b-chat',
  'glm-4',
  'glm-4-flash',
]

const isFormValid = computed(() => {
  return form.value.name && form.value.base_url && form.value.api_key
})

async function handleCreate() {
  if (!isFormValid.value) return

  creating.value = true
  try {
    const instance = await providerStore.createCustomProvider(form.value)
    if (instance) {
      emit('created', instance)
      visible.value = false
      resetForm()
    }
  } catch (error) {
    const err = error as Error
    ElMessage.error(`Failed to create provider: ${err.message || String(error)}`)
  } finally {
    creating.value = false
  }
}

function resetForm() {
  form.value = {
    name: '',
    provider_type: 'newapi',
    base_url: '',
    api_key: '',
    models: [],
  }
}

watch(visible, (val) => {
  if (!val) {
    resetForm()
  }
})
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
