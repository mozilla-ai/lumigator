<template>
  <div>
    <h3>Settings</h3>
    <h4>API Keys</h4>
    <p>To use API-based models in Lumigator, add your API keys.</p>

    <div class="">
      <label for="mistral_api_key">Mistral</label>
      <div>
        <InputText
          id="mistral_api_key"
          :disabled="getApiKeyRef('mistral_api_key').value === maskedValue"
          v-model="getApiKeyRef('mistral_api_key').value"
          aria-describedby="Mistral API Key"
          placeholder="Mistral API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'mistral_api_key',
              description: 'Mistral API Key',
              value: getApiKeyRef('mistral_api_key').value,
            })
          "
          label="Save"
        ></Button>
        <Button @click="deleteSecret('mistral_api_key')" label="Delete"></Button>
      </div>
    </div>
    <div class="">
      <label for="openai_api_key">OPENAI</label>
      <div>
        <InputText
          id="openai_api_key"
          :disabled="getApiKeyRef('openai_api_key').value === maskedValue"
          v-model="getApiKeyRef('openai_api_key').value"
          aria-describedby="OpenAI API Key"
          placeholder="OpenAI API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'openai_api_key',
              description: 'OpenAI API Key',
              value: getApiKeyRef('openai_api_key').value,
            })
          "
          label="Save"
        ></Button>
        <Button @click="deleteSecret('openai_api_key')" label="Delete"></Button>
      </div>
    </div>
    <div class="">
      <label for="huggingface_api_key">Hugging Face</label>
      <div>
        <InputText
          id="huggingface_api_key"
          :disabled="getApiKeyRef('huggingface_api_key').value === maskedValue"
          v-model="getApiKeyRef('huggingface_api_key').value"
          aria-describedby="Hugging Face API Key"
          placeholder="Hugging Face API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'huggingface_api_key',
              description: 'Hugging Face API Key',
              value: getApiKeyRef('huggingface_api_key').value,
            })
          "
          label="Save"
        >
        </Button>
        <Button @click="deleteSecret('huggingface_api_key')" label="Delete"></Button>
      </div>
    </div>
    <div class="">
      <label for="deepseek_api_key">DeepSeek</label>
      <div>
        <InputText
          id="deepseek_api_key"
          :disabled="getApiKeyRef('deepseek_api_key').value === maskedValue"
          v-model="getApiKeyRef('deepseek_api_key').value"
          aria-describedby="DeepSeek Face API Key"
          placeholder="DeepSeek Face API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'deepseek_api_key',
              description: 'DeepSeek Face API Key',
              value: getApiKeyRef('deepseek_api_key').value,
            })
          "
          label="Save"
        ></Button>
        <Button @click="deleteSecret('deepseek_api_key')" label="Delete"></Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { settingsService } from '@/sdk/settingsService'
import type { SecretUploadPayload } from '@/types/Secret'
import { InputText } from 'primevue'
import Button from 'primevue/button'
import { onMounted, ref, type Ref } from 'vue'

// Placeholder for configured secrets where the actual value is hidden
const maskedValue = '****************';

// API key map is used to track API key names and their corresponding values
const apiKeyMap = new Map<string, Ref<string>>()
apiKeyMap.set('mistral_api_key', ref(''))
apiKeyMap.set('openai_api_key', ref(''))
apiKeyMap.set('huggingface_api_key', ref(''))
apiKeyMap.set('deepseek_api_key', ref(''))

// Return the Ref directly, defaulting to an empty ref if not found
const getApiKeyRef = (key: string): Ref<string> => {
  return apiKeyMap.get(key) ?? ref('');
};

onMounted(async () => {
  fetchSecrets()
})

const fetchSecrets = async () => {
  const secrets = await settingsService.fetchSecrets()
  apiKeyMap.forEach((ref, secretKey) => {
    const secret = secrets.find((secret) => secret.name == secretKey)
    ref.value = secret ? maskedValue : ''
  })
}

const deleteSecret = async (key: string) => {
  await settingsService.deleteSecret(key)
  const correspondingSecretKeyRef = apiKeyMap.get(key)
  if (correspondingSecretKeyRef) {
    correspondingSecretKeyRef.value = ''
  }
}

const uploadSecret = async (secret: SecretUploadPayload) => {
  await settingsService.uploadSecret(secret)
  const correspondingSecretKeyRef = apiKeyMap.get(secret.name)
  if (correspondingSecretKeyRef) {
    correspondingSecretKeyRef.value = maskedValue
  }

}

// TODO: How to stop the user accidentally saving over a legit secret with *********?
</script>

<style scoped></style>
