import axios from 'axios'

export const lumigatorApiAxiosInstance = axios.create({
  baseURL: '/api/v1/', // Set to relative path to the backend
  headers: {
    'Content-Type': 'application/json',
  },
})
