import axios from 'axios';

const http = axios.create({
  baseURL: 'http://localhost:8000/api/v1/', // API base URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default http;

// http://localhost:8000/api/v1/datasets/