import http from '@/services/http';
import { PATH_HEALTH_ROOT, PATH_HEALTH_JOB_METADATA } from './api';

async function fetchHealthStatus() {
    try {
    const response = await http.get(PATH_HEALTH_ROOT());
    return response.data.status
  } catch (error) {
    console.log(error);
    return error;
  }
}
async function fetchJobStatus(id) {
  try {
    const response = await http.get(PATH_HEALTH_JOB_METADATA(id));
    return response.data.status
  } catch (error) {
    console.log(error);
    return error;
  }
}

export default {
  fetchHealthStatus,
  fetchJobStatus
}
