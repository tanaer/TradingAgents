<template>
  <el-dialog
    v-model="visible"
    :title="`Configure ${provider?.name || 'Provider'}`"
    width="500px"
  >
    <el-form :model="form" label-width="100px" v-if="provider">
      <el-form-item label="API Key">
        <el-input
          v-model="form.api_key"
          type="password"
          show-password
          placeholder="Enter your API key"
        />
      </el-form-item>

      <el-form-item label="Base URL" v-if="provider.id === 'newapi'">
        <el-input
          v-model="form.base_url"
          placeholder="https://your-api-endpoint.com/v1"
        />
      </el-form-item>

      <el-form-item label="Test Model">
        <el-select v-model="form.test_model" placeholder="Select model for testing">
          <el-option
            v-for="model in provider.models"
            :key="model"
            :label="model"
            :value="model"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">Cancel</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">
        Save Configuration
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ProviderInfo } from '@/types'
import { useProviderStore } from '@/stores'

const props = defineProps<{
  modelValue: boolean
  provider: ProviderInfo | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const providerStore = useProviderStore()
const saving = ref(false)

const form = ref({
  api_key: '',
  base_url: '',
  test_model: '',
})

const visible = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

watch(() => props.provider, (provider) => {
  if (provider) {
    form.value.test_model = provider.models[0] || ''
    form.value.base_url = provider.base_url || ''
  }
})

async function handleSave() {
  if (!props.provider) return

  saving.value = true
  try {
    const success = await providerStore.configureProvider({
      provider_id: props.provider.id,
      api_key: form.value.api_key,
      base_url: form.value.base_url || undefined,
    })

    if (success) {
      visible.value = false
      form.value.api_key = ''
    }
  } finally {
    saving.value = false
  }
}
</script>
