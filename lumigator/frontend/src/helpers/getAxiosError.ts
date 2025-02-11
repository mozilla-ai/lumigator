import type { AxiosError } from 'axios'
import axios from 'axios'

/**
 * Extracts a meaningful error message from various types of thrown errors.
 * Handles Axios errors, standard JavaScript errors, and unexpected non-error objects.
 *
 * @param error - The error object that was caught.
 * @returns A string representing the error message.
 */
export const getAxiosError = (error: Error | AxiosError): string => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with an error status (e.g., 400, 500)
      return error.response.data
        ? JSON.stringify(error.response.data, null, 2)
        : `Error ${error.response.status}: ${error.response.statusText}`
    } else if (error.request) {
      // No response received (e.g., network issues, server down)
      return 'No response from server. Please check your connection or if the server is up.'
    } else {
      // Something went wrong setting up the request
      return error.message || 'An unexpected Axios error occurred.'
    }
  } else {
    // Check if it's a standard JavaScript error
    return error.message
  }
}
