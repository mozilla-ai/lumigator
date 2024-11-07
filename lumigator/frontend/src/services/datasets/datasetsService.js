import http from '@/services/http';
import { PATH_GET_ALL_DATASETS } from './api';

async function fetchDatasets() {
	const response = await http.get(PATH_GET_ALL_DATASETS())
	console.log(response.data);
	return response.data.items;
}

export default {
	fetchDatasets
}