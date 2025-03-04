import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { Secret, SecretUploadPayload } from '@/types/Secret'

const PATH_SETTINGS_ROOT = 'settings'
const PATH_SECRETS_ROOT = `${PATH_SETTINGS_ROOT}/secrets`
const PATH_SECRET = (secretName: string) => `${PATH_SECRETS_ROOT}/${secretName}`

/**
 * Deletes a secret by name.
 * @param {string} secretName - The name of the secret.
 */
export async function deleteSecret(secretName: string): Promise<void> {
  return lumigatorApiAxiosInstance.delete(PATH_SECRET(secretName))
}

/**
 * Fetches the names and descriptions of all secrets configured by the user.
 * @returns The list of secrets (without their values).
 */
export async function fetchSecrets(): Promise<Secret[]> {
  const response = await lumigatorApiAxiosInstance.get(PATH_SECRETS_ROOT)

  return response.data
}

/**
 * Uploads a secret (creates/updates).
 * @param {string} id - The secret definition (name and description).
 * @param {string} value - The (sensitive) value of the secret.
 */
export async function uploadSecret(secret: SecretUploadPayload): Promise<void> {
  return lumigatorApiAxiosInstance.put(PATH_SECRET(secret.name), {
    description: secret.description,
    value: secret.value,
  })
}

export const settingsService = {
  deleteSecret,
  fetchSecrets,
  uploadSecret,
}
