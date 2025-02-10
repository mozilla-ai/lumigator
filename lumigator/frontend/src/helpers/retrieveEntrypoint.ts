import type { Job } from '@/types/Experiment'

/**
 * Retrieves and normalizes the entrypoint configuration from a job object.
 *
 * @param {Object} job - The job object containing the entrypoint.
 * @param {string} job.entrypoint - The entrypoint stringified JSON provided from the API
 * @returns {Object|null} The parsed and normalized entrypoint configuration object, or null if invalid.
 */
export function retrieveEntrypoint(job: Job) {
  if (!job || !job.entrypoint) {
    console.error('Invalid job data')
    return
  }

  // Extract stringified JSON from entrypoint property
  // refer to docs @http://localhost:8000/docs#/health/get_job_metadata_api_v1_health_jobs__job_id__get
  const inputString = job.entrypoint
  const configString = inputString.split('--config')[1]?.trim()

  if (!configString) {
    console.error('No config found in job entrypoint')
    return
  }

  try {
    const jsonObject = JSON.parse(configString.replace(/^'/, '').replace(/'$/, ''))
    jsonObject.dataset = {
      id: jsonObject.dataset.path.match(/datasets\/([^/]+)\/([^/]+)/)?.[1],
      name: jsonObject.dataset.path.match(/datasets\/([^/]+)\/([^/]+)/)?.[2],
    }
    jsonObject.name = jsonObject.name.split('/')[0]

    // NOTE: Normalization is required because the config templates used per-model sometimes vary,
    // meaning that the location of the data we are trying to parse isn't always the same.
    // See: lumigator/backend/backend/config_templates.py

    // Normalize the max_samples
    if (typeof jsonObject?.job?.max_samples !== 'undefined') {
      jsonObject.max_samples = jsonObject.job.max_samples
    } else if (typeof jsonObject?.evaluation?.max_samples !== 'undefined') {
      jsonObject.max_samples = jsonObject.evaluation.max_samples
    } else {
      throw new Error('Unable to parse max_samples from entrypoint config: ' + configString)
    }

    // Normalize the model path
    let modelPath = ''
    if (jsonObject?.model?.path) {
      modelPath = jsonObject.model.path
    } else if (jsonObject?.model?.inference?.engine) {
      modelPath = jsonObject.model.inference.engine
    } else if (jsonObject?.hf_pipeline?.model_uri) {
      modelPath = jsonObject.hf_pipeline.model_uri
    } else if (jsonObject?.inference_server?.engine) {
      modelPath = jsonObject.inference_server.engine
    } else {
      throw new Error('Unable to parse model path from entrypoint config: ' + configString)
    }

    ;(jsonObject.model ??= {}).path = modelPath

    return jsonObject
  } catch (error) {
    console.error('Failed to parse JSON in entrypoint:', error)
    return
  }
}
