/**
 * Represents a secret with a name and description.
 */
export interface Secret {
  name: string
  description: string
}

/**
 * Represents an uploadable secret, extending the base secret
 * with an additional value field for the secret's content.
 */
export interface SecretUploadPayload extends Secret {
  value: string
}
