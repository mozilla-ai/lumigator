import axios from 'axios'
import { getAxiosError } from './getAxiosError'

export const lumigatorApiAxiosInstance = axios.create({
  baseURL: '/api/v1/', // Set to relative path to the backend
  headers: {
    'Content-Type': 'application/json',
  },
})

lumigatorApiAxiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error(getAxiosError(error))

    throw error
  },
)
