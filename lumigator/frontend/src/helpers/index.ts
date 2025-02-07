import type { Job } from '@/types/Experiment'

/**
 * Formats a date string into 'dd-MMM-yyyy, hh:mm' format.
 *
 * @param {string} dateString - The date string to format.
 * @returns {string} The formatted date string.
 */
export function formatDate(dateString: string) {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
    .format(date)
    .replace(/(\d{4})(\s)/, '$1,$2')
}

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

/**
 * Calculates the duration between two ISO timestamps and formats it as 'hh:mm:ss'.
 * It is used for calculating the duration of jobs OR Experiments until Backend provides this info
 * @param {string} start - The start timestamp in ISO format.
 * @param {string} finish - The finish timestamp in ISO format.
 * @returns {string} The formatted duration as 'hh:mm:ss'.
 * @throws {Error} If the date format is invalid.
 */
export function calculateDuration(start: string, finish: string) {
  // Calculate the time difference in milliseconds
  const differenceInMilliseconds = new Date(finish).getTime() - new Date(start).getTime()

  if (isNaN(differenceInMilliseconds)) {
    throw new Error('Invalid date format. Please provide valid ISO timestamps.')
  }

  const totalSeconds = Math.floor(differenceInMilliseconds / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  // Format the result as hh:mm:ss
  const formatedDuration = `${String(hours).padStart(2, '0')}:
  ${String(minutes).padStart(2, '0')}:
  ${String(seconds).padStart(2, '0')}`
  return formatedDuration
}

/**
 * Initiates a download of the provided content as a file.
 * Used for downloading Resluts and Datasets
 * @param {Blob} blob - The content to download.
 * @param {string} filename - The name of the file to be downloaded.
 */
export function downloadContent(blob: Blob, filename: string) {
  const downloadUrl = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.className = 'hidden'
  anchor.href = downloadUrl
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  URL.revokeObjectURL(downloadUrl)
  document.body.removeChild(anchor)
}
