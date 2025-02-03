import http from '@/services/http';
import { PATH_MODELS_ROOT } from './api';

async function fetchModels(task_name = 'summarization') {
  try {
    const response = await http.get(PATH_MODELS_ROOT(task_name))
    if (response) {
      return response.data.items;
    }
  } catch (error) {
    console.error('Fetching Models failed.', { cause: error });
    throw error;
  }
}

export default {
  fetchModels
}
