<template>
  <div class="settings-container">
    <div>
      <h3 class="settings-title">Settings</h3>
    </div>
    <div class="api-keys-container">
      <div class="api-keys-header">
        <h4 class="api-keys-title">API Keys</h4>
        <p class="api-keys-description">
          To help improve Lumigator, you can choose to share completely anonymized usage data. We do
          not profile you or track your location or web activity.
          <a
            href="https://mozilla-ai.github.io/lumigator/get-started/quickstart.html#get-the-results"
            class="learn-more-link"
            rel="noopener"
            target="_blank"
            >Learn more
          </a>
        </p>
      </div>

      <div class="api-keys">
        <div class="api-key">
          <label class="api-key-label" for="mistral_api_key">Mistral</label>
          <div class="api-key-field">
            <div style="position: relative; display: flex; flex: 1">
              <InputText
                class="api-key-input"
                fluid
                id="mistral_api_key"
                :disabled="getApiKeyRef('mistral_api_key').value === maskedValue"
                v-model="getApiKeyRef('mistral_api_key').value"
                aria-describedby="Mistral API Key"
                placeholder="Mistral API Key"
              />
              <Button
                class="delete-button button"
                icon="pi pi-trash"
                @click="deleteSecret('mistral_api_key')"
                v-if="
                  getApiKeyRef('mistral_api_key').value &&
                  getApiKeyRef('mistral_api_key').value !== maskedValue
                "
              ></Button>
            </div>
            <Button
              class="save-button button"
              @click="
                uploadSecret({
                  name: 'mistral_api_key',
                  description: 'Mistral API Key',
                  value: getApiKeyRef('mistral_api_key').value,
                })
              "
              label="Save"
            ></Button>
          </div>
        </div>
        <div class="api-key">
          <label class="api-key-label" for="openai_api_key">OPENAI</label>
          <div class="api-key-field">
            <div style="position: relative; display: flex; flex: 1">
              <InputText
                class="api-key-input"
                fluid
                id="openai_api_key"
                :disabled="getApiKeyRef('openai_api_key').value === maskedValue"
                v-model="getApiKeyRef('openai_api_key').value"
                aria-describedby="OpenAI API Key"
                placeholder="OpenAI API Key"
              />
              <Button
                class="delete-button button"
                icon="pi pi-trash"
                @click="deleteSecret('openai_api_key')"
                v-if="isApiKeyRegistered('openai_api_key')"
              ></Button>
            </div>
            <Button
              class="save-button button"
              @click="
                uploadSecret({
                  name: 'openai_api_key',
                  description: 'OpenAI API Key',
                  value: getApiKeyRef('openai_api_key').value,
                })
              "
              label="Save"
            ></Button>
          </div>
        </div>
        <div class="api-key">
          <label class="api-key-label" for="huggingface_api_key">Hugging Face</label>
          <div class="api-key-field">
            <div style="position: relative; display: flex; flex: 1">
              <InputText
                class="api-key-input"
                fluid
                id="huggingface_api_key"
                :disabled="getApiKeyRef('huggingface_api_key').value === maskedValue"
                v-model="getApiKeyRef('huggingface_api_key').value"
                aria-describedby="Hugging Face API Key"
                placeholder="Hugging Face API Key"
              />
              <Button
                class="delete-button button"
                icon="pi pi-trash"
                @click="deleteSecret('huggingface_api_key')"
                v-if="
                  getApiKeyRef('huggingface_api_key').value &&
                  getApiKeyRef('huggingface_api_key').value !== maskedValue
                "
              ></Button>
            </div>
            <Button
              class="save-button button"
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
          </div>
        </div>
        <div class="api-key">
          <label class="api-key-label" for="deepseek_api_key">DeepSeek</label>
          <div class="api-key-field">
            <div style="position: relative; display: flex; flex: 1">
              <InputText
                class="api-key-input"
                fluid
                id="deepseek_api_key"
                :disabled="getApiKeyRef('deepseek_api_key').value === maskedValue"
                v-model="getApiKeyRef('deepseek_api_key').value"
                aria-describedby="DeepSeek Face API Key"
                placeholder="DeepSeek Face API Key"
              />
              <Button
                class="delete-button button"
                icon="pi pi-trash"
                @click="deleteSecret('deepseek_api_key')"
                v-if="
                  getApiKeyRef('deepseek_api_key').value &&
                  getApiKeyRef('deepseek_api_key').value !== maskedValue
                "
              ></Button>
            </div>
            <Button
              class="save-button button"
              @click="
                uploadSecret({
                  name: 'deepseek_api_key',
                  description: 'DeepSeek Face API Key',
                  value: getApiKeyRef('deepseek_api_key').value,
                })
              "
              label="Save"
            ></Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { settingsService } from '@/sdk/settingsService'
import type { SecretUploadPayload } from '@/types/Secret'
import { InputText } from 'primevue'
import Button from 'primevue/button'
import { isReactive, onMounted, ref, type Ref } from 'vue'

// Placeholder for configured secrets where the actual value is hidden.
const maskedValue = '****************'

// API key map is used to track API key names to their corresponding ref and whether the setting exists remotely.
const apiKeyMap = new Map<string, { reference: Ref<string>, existsRemotely: boolean }>([
  ['mistral_api_key', { reference: ref(''), existsRemotely: false }],
  ['openai_api_key', { reference: ref(''), existsRemotely: false }],
  ['huggingface_api_key', { reference: ref(''), existsRemotely: false }],
  ['deepseek_api_key', { reference: ref(''), existsRemotely: false }],
])

onMounted(async () => {
  fetchSecrets()
})

// Return the Ref directly, defaulting to an empty ref if not found.
const getApiKeyRef = (key: string): Ref<string> => {
  return apiKeyMap.get(key)?.reference ?? ref('')
}

// Retrieve whether the API key exists remotely.
const isApiKeyRegistered = (key: string): boolean => {
  return apiKeyMap.get(key)?.existsRemotely ?? false
}

// Check if the API key is valid (e.g. it is some characters, but not the masked value).
const isValidApiKey = (value: string): boolean => {
  return value !== maskedValue && value.length > 0
}

const fetchSecrets = async () => {
  const secrets = await settingsService.fetchSecrets()
  apiKeyMap.forEach((obj, secretKey) => {
    obj.existsRemotely = secrets.some((secret) => secret.name == secretKey)
    obj.reference.value = obj.existsRemotely ? maskedValue : ''
  })
}

const deleteSecret = async (key: string) => {
  await settingsService.deleteSecret(key)
  const correspondingSecretKeyRef = apiKeyMap.get(key)
  if (correspondingSecretKeyRef) {
    correspondingSecretKeyRef.reference.value = ''
    correspondingSecretKeyRef.existsRemotely = false
  }
}

const uploadSecret = async (secret: SecretUploadPayload) => {
  await settingsService.uploadSecret(secret)
  const correspondingSecretKeyRef = apiKeyMap.get(secret.name)
  if (correspondingSecretKeyRef) {
    correspondingSecretKeyRef.reference.value = maskedValue
    correspondingSecretKeyRef.existsRemotely = true
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/variables';
@use '@/styles/mixins';

.settings-title {
  @include mixins.heading-2;
  color: variables.$l-grey-100;
  margin-bottom: 2.5rem;
}

.settings-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  margin: 0 auto;
  text-align: left;
  padding: 2.5rem 1.5rem;
}

.api-keys-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.api-keys-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.api-keys-description {
  @include mixins.caption;
  color: variables.$l-grey-100;
}
.learn-more-link {
  font-weight: 700;
}

.api-keys {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.api-keys-title {
  @include mixins.paragraph-2;
  color: variables.$white;
}

.api-key-label {
  @include mixins.captions-caps;
  color: variables.$l-grey-100;
}

.api-key {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.api-key-field {
  display: flex;
  gap: 1rem;
}

.save-button {
  border-radius: 2.875rem;
}

.save-button:disabled {
  background-color: variables.$l-grey-300;
  color: variables.$l-grey-200;
  border: 0.5px solid variables.$border-stroke;
}

.delete-button {
  position: absolute;
  fill: variables.$l-grey-100;
  background-color: inherit;
  vertical-align: middle;
  border: none;
  right: 0;
  top: 0;
  color: variables.$l-grey-100;
}

.delete-button:hover {
  background: none;
}

.api-key-input {
  border-radius: 2rem;
  border: 0.5px solid variables.$border-stroke;
  background: variables.$l-grey-300;

  /* shadow/neutral/sm */
  box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, 0.05);
}

.api-key-input::placeholder {
  @include mixins.text-small;
  color: variables.$l-grey-200;
}
</style>
