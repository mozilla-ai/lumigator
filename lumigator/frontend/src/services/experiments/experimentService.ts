import http from '@/services/http'
import {
  PATH_JOBS_ROOT,
  PATH_EXPERIMENTS_EVALUATE,
  PATH_JOB_DETAILS,
  PATH_EXPERIMENT_RESULTS,
  PATH_EXPERIMENT_LOGS,
  PATHS_EXPERIMENTS_ANNOTATE,
} from './api'
import type { Job, ObjectData } from '@/types/Experiment'
import { AxiosError } from 'axios'

/**
 *
 * @returns {array} of all jobs, regardless the experiment
 */
async function fetchJobs(): Promise<Job[]> {
  try {
    const response = await http.get(PATH_JOBS_ROOT())
    return response.data.items.map((job: Job) => ({
      ...job,
      status: job.status.toUpperCase(),
    }))
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error fetching experiments', error.message)
    } else {
      console.error('Error fetching experiments', error)
    }
    return []
  }
}

/**
 * Fetches details of a specific job by ID.
 * @param {string} id - The ID of the job.
 */

// TODO: Remame fetchJobDetails and refactor accodingly

async function fetchExperimentDetails(id: string) {
  try {
    const response = await http.get(PATH_JOB_DETAILS(id))
    if (response?.data?.status) {
      // Ensure that we transform status at the point the API returns it.
      response.data.status = response.data.status.toUpperCase()
    }
    return response.data
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error fetching experiment details', error.message)
    } else {
      console.error('Error fetching experiment details', error)
    }
    return
  }
}

async function fetchJobStatus(id: string) {
  const job = await fetchExperimentDetails(id)
  return job?.status
}

/**
 * Triggers a new experiment with the given payload, due API limitations at the time.
 * In fact this funcition triggers an evaluation job.
 * @param {Object} experimentPayload - The payload for the experiment.
 *  The schema of experimentPayload can be found @ api/v1/experiments/
 */
// TODO: For experiments with multiple models this function is called recursively for every model selected from the form.
// Check ExperimentForm.vue
async function triggerExperiment(experimentPayload: unknown) {
  try {
    const response = await http.post(PATH_EXPERIMENTS_EVALUATE(), experimentPayload, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  } catch (error) {
    console.error('Error while creating experiment', error)
    if (error instanceof Error) {
      return error.message
    } else if (error instanceof AxiosError) {
      return error.response?.data
    }
  }
}

async function triggerAnnotationJob(groundTruthPayload: unknown) {
  try {
    const response = await http.post(PATHS_EXPERIMENTS_ANNOTATE(), groundTruthPayload, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  } catch (error) {
    console.error('Error while creating ground truth job', error)
    return
  }
}
export { triggerAnnotationJob }

/**
 * Fetches the results of a specific job.
 * @param {string} job_id
 */
async function fetchResults(
  job_id: string,
): Promise<unknown | { resultsData: ObjectData; id: string; download_url: string }> {
  try {
    const response = await http.get(PATH_EXPERIMENT_RESULTS(job_id))
    const { download_url, id } = response.data
    if (!download_url) {
      console.error('No download_url found in the response.')
      return
    }
    const jsonData = await http.get(download_url)
    return {
      resultsData: jsonData.data,
      id,
      download_url,
    }
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error fetching experiment results', error.message || error)
    } else {
      console.error('Error fetching experiment results', error)
    }

    //TODO: this should throw to the consumer
    return error
  }
}

/**
 * Downloads the results of a specific experiment by ID.
 * @param {string} experiment_id .
 * @returns {Promise<Blob|Error>} A promise that resolves to a Blob containing the file data.
 */
async function downloadResults(experiment_id: string) {
  try {
    const response = await http.get(PATH_EXPERIMENT_RESULTS(experiment_id))
    const { download_url } = response.data
    if (!download_url) {
      console.error('No download_url found in the response.')
      return
    }
    const fileResponse = await http.get(download_url, {
      responseType: 'blob', // Important: Receive the file as a binary blob
    })
    const blob = fileResponse.data
    return blob
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error downloading experiment results', error.message || error)
    } else if (error instanceof AxiosError) {
      console.error('Error downloading experiment results', error.response?.data)
    }

    // TODO: propagate the error to the consumer
    return error
  }
}

/**
 * Fetches the logs of a specific job by ID.
 * @param {string} id .
 */
async function fetchLogs(id: string) {
  try {
    const logsResponse = await http.get(PATH_EXPERIMENT_LOGS(id))
    return logsResponse.data
  } catch (error) {
    console.error('Error fetching logs for job', id, error)
  }
}

export default {
  fetchJobs,
  fetchJobStatus,
  fetchResults,
  downloadResults,
  fetchExperimentDetails,
  triggerExperiment,
  triggerAnnotationJob,
  fetchLogs,
}
