import axios from 'axios'

const http = axios.create({
  baseURL: '/api/v1/', // Set to relative path to the backend
  headers: {
    'Content-Type': 'application/json',
  },
})

export default http
