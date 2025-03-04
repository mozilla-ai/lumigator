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
          :disabled="mistralApiKey === magicStars"
          v-model="mistralApiKey"
          aria-describedby="Mistral API Key"
          placeholder="Mistral API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'mistral_api_key',
              description: 'Mistral API Key',
              value: mistralApiKey,
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
          :disabled="openAIApiKey === magicStars"
          v-model="openAIApiKey"
          aria-describedby="OpenAI API Key"
          placeholder="OpenAI API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'openai_api_key',
              description: 'OpenAI API Key',
              value: openAIApiKey,
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
          :disabled="huggingFaceApiKey === magicStars"
          v-model="huggingFaceApiKey"
          aria-describedby="Hugging Face API Key"
          placeholder="Hugging Face API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'huggingface_api_key',
              description: 'Hugging Face API Key',
              value: huggingFaceApiKey,
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
          :disabled="deepSeekApiKey === magicStars"
          v-model="deepSeekApiKey"
          aria-describedby="DeepSeek Face API Key"
          placeholder="DeepSeek Face API Key"
        />
        <Button
          @click="
            uploadSecret({
              name: 'deepseek_api_key',
              description: 'DeepSeek Face API Key',
              value: deepSeekApiKey,
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
import type { Secret, SecretUploadPayload } from '@/types/Secret'
import { InputText } from 'primevue'
import Button from 'primevue/button'

import { onMounted, ref, type Ref } from 'vue'
// Configured secrets
const secrets: Ref<Secret[]> = ref([])
// Form fields
const mistralApiKey = ref()
const openAIApiKey = ref()
const huggingFaceApiKey = ref()
const deepSeekApiKey = ref()

// TODO: this cannot be called magic stars
const magicStars = '****************'

// TODO: rename this nicely, and make the map linked up all nice ;)
const myMap = new Map<string, Ref<string>>()
myMap.set('mistral_api_key', mistralApiKey)
myMap.set('openai_api_key', openAIApiKey)
myMap.set('huggingface_api_key', huggingFaceApiKey)
myMap.set('deepseek_api_key', deepSeekApiKey)

onMounted(async () => {
  fetchSecrets()
  console.log(secrets.value)
})

const fetchSecrets = async () => {
  const secrets = await settingsService.fetchSecrets()
  myMap.forEach((ref, secretKey) => {
    const secret = secrets.find((secret) => secret.name == secretKey)
    ref.value = secret ? magicStars : ''
  })
}

const deleteSecret = async (key: string) => {
  await settingsService.deleteSecret(key)
  const correspondingSecretKeyRef = myMap.get(key)
  if (correspondingSecretKeyRef) {
    correspondingSecretKeyRef.value = ''
  }
}

const uploadSecret = async (secret: SecretUploadPayload) => {
  await settingsService.uploadSecret(secret)
  const correspondingSecretKeyRef = myMap.get(secret.name)
  if (correspondingSecretKeyRef) {
    correspondingSecretKeyRef.value = magicStars
  }

}

// TODO: How to stop the user accidentally saving over a legit secret with *********?
</script>

<style scoped></style>
