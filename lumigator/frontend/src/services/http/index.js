import axios from 'axios';

const http = axios.create({
  baseURL: import.meta.env.VUE_APP_BASE_URL, // API baseURL as env variable
  headers: {
    'Content-Type': 'application/json',
  },
});

export default http;
