<template>
  <div class="settings-container">
    <div>
      <h3 class="settings-title">Settings</h3>
    </div>
    <div class="api-keys-container">
      <div class="api-keys-header">
        <h4 class="api-keys-title">API Keys</h4>
        <p class="api-keys-description">
          To use API-based models in Lumigator, add your API keys.
          <a
            href="https://mozilla-ai.github.io/lumigator/operations-guide/configuration.html#api-settings"
            class="learn-more-link"
            rel="noopener"
            target="_blank"
            >Learn more
          </a>
        </p>
      </div>

      <div class="api-keys">
        <div
          class="api-key"
          v-for="[apiKey, { reference, existsRemotely, title }] in apiKeyMap.entries()"
          :key="apiKey"
        >
          <label class="api-key-label" :for="apiKey">{{ title }}</label>
          <div class="api-key-field">
            <div style="position: relative; display: flex; flex: 1">
              <InputText
                @focus="handleFocus(apiKey)"
                @blur="handleBlur(apiKey)"
                autocomplete="off"
                class="api-key-input"
                fluid
                :id="apiKey"
                v-model="reference.value"
                aria-describedby="api-key-label"
                :placeholder="`${title} API Key`"
              />
              <Button
                class="delete-button button"
                icon="pi pi-trash"
                @click="deleteSecret(apiKey, title)"
                v-if="existsRemotely"
              ></Button>
            </div>
            <Button
              class="save-button button"
              @click="
                uploadSecret(
                  {
                    name: apiKey,
                    description: `${title} API Key`,
                    value: reference.value,
                  },
                  title,
                )
              "
              :disabled="!isValidApiKey(reference.value)"
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
import { InputText, type ToastMessageOptions } from 'primevue'
import Button from 'primevue/button'
import { onMounted, ref, type Ref } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import axios, { AxiosError } from 'axios'
import { getAxiosError } from '@/helpers/getAxiosError'

const confirm = useConfirm()
const toast = useToast()
// Placeholder for configured secrets where the actual value is hidden.
const maskedValue = '****************'

// API key map is used to track API key names (based on the provider name) to their corresponding ref, title and whether the setting exists remotely.
const apiKeyMap = new Map<
  string,
  { reference: Ref<string>; existsRemotely: boolean; title: string }
>([
  ['mistral_api_key', { reference: ref(''), existsRemotely: false, title: 'Mistral' }],
  ['openai_api_key', { reference: ref(''), existsRemotely: false, title: 'OpenAI' }],
  ['hf_api_key', { reference: ref(''), existsRemotely: false, title: 'Hugging Face' }],
  ['deepseek_api_key', { reference: ref(''), existsRemotely: false, title: 'DeepSeek' }],
])

onMounted(async () => {
  fetchSecrets()
})

// Check if the API key is valid (e.g. it is some characters, but not the masked value).
const isValidApiKey = (value: string): boolean => {
  return value !== maskedValue && value.length > 0
}

const fetchSecrets = async () => {
  try {
    const secrets = await settingsService.fetchSecrets()
    apiKeyMap.forEach((obj, secretKey) => {
      obj.existsRemotely = secrets.some((secret) => secret.name == secretKey)
      obj.reference.value = obj.existsRemotely ? maskedValue : ''
    })
  } catch (error) {
    const msg = extractErrorMessages(error).join(', ')
    toast.add({
      severity: 'error',
      summary: 'Unable to fetch configured API keys',
      detail: `${msg}`,
      messageicon: 'pi pi-exclamation-triangle',
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })
  }
}

const deleteSecret = async (key: string, title: string) => {
  confirm.require({
    header: 'Delete API key?',
    message: `${title} API key`,
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true,
    },
    acceptProps: {
      label: 'Delete',
      severity: 'danger',
    },
    accept: async () => {
      try {
        // Delete the secret from the backend.
        await settingsService.deleteSecret(key)

        toast.add({
          severity: 'success',
          summary: `${title} API key deleted`,
          messageicon: 'pi pi-trash',
          detail: key,
          group: 'br',
          life: 3000,
        } as ToastMessageOptions & { messageicon: string })

        // Update the state of the reference.
        const correspondingSecretKeyRef = apiKeyMap.get(key)
        if (correspondingSecretKeyRef) {
          correspondingSecretKeyRef.reference.value = ''
          correspondingSecretKeyRef.existsRemotely = false
        }
      } catch (error) {
        const msg = extractErrorMessages(error).join(', ')
        toast.add({
          severity: 'error',
          summary: `Unable to delete ${title} API key`,
          detail: `${msg}`,
          messageicon: 'pi pi-exclamation-triangle',
          group: 'br',
          life: 3000,
        } as ToastMessageOptions & { messageicon: string })
      }
    },
    reject: () => {},
  })
}

const uploadSecret = async (secret: SecretUploadPayload, title: string) => {
  try {
    // Upload the secret to the backend.
    await settingsService.uploadSecret(secret)

    toast.add({
      severity: 'success',
      summary: `${title} API key saved`,
      messageicon: 'pi pi-save',
      detail: secret.name,
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })

    // Update the state of the reference.
    const correspondingSecretKeyRef = apiKeyMap.get(secret.name)
    if (correspondingSecretKeyRef) {
      correspondingSecretKeyRef.reference.value = maskedValue
      correspondingSecretKeyRef.existsRemotely = true
    }
  } catch (error) {
    // Extract the error messages from the error object.
    const msg = extractErrorMessages(error).join(', ')
    toast.add({
      severity: 'error',
      summary: `Unable to save ${title} API key`,
      detail: `${msg}`,
      messageicon: 'pi pi-exclamation-triangle',
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })
  }
}

function extractErrorMessages(error: unknown): string[] {
  if (
    axios.isAxiosError(error) &&
    error.response?.status === 422 &&
    Array.isArray(error.response?.data?.detail)
  ) {
    return error.response.data.detail.flatMap((item: { msg?: string }) =>
      item.msg ? [item.msg] : [],
    )
  } else {
    return [getAxiosError(error as Error | AxiosError)]
  }
}

const handleFocus = (key: string) => {
  const correspondingSecretKeyRef = apiKeyMap.get(key)
  if (correspondingSecretKeyRef?.existsRemotely) {
    correspondingSecretKeyRef.reference.value = ''
  }
}

const handleBlur = (key: string) => {
  const correspondingSecretKeyRef = apiKeyMap.get(key)
  if (
    correspondingSecretKeyRef?.reference.value === '' &&
    correspondingSecretKeyRef.existsRemotely
  ) {
    correspondingSecretKeyRef.reference.value = maskedValue
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
  color: variables.$l-grey-100;
}

.delete-button:hover,
.delete-button:focus,
.delete-button:focus-visible,
.delete-button:active {
  background: none;
  border: none;
  outline: none;
  // color: #E0C414;
  color: red;
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
