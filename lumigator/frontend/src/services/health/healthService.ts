import http from '@/services/http';
import { PATH_HEALTH_ROOT } from './api';

async function fetchHealthStatus() {
  try {
    const response = await http.get(PATH_HEALTH_ROOT());
    return response.data.status;
  } catch (error) {
    console.error('Error getting health status', error);
    return error;
  }
}

export default {
  fetchHealthStatus,
};
