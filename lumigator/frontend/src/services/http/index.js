import axios from 'axios';

const http = axios.create({
  baseURL: '/api/v1/', // API baseURL as env variable
  headers: {
    'Content-Type': 'application/json',
  },
});

export default http;
