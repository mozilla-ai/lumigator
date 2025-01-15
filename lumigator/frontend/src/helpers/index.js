export function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(date).replace(/(\d{4})(\s)/, '$1,$2');
}

export function retrieveEntrypoint(job) {
  if (!job || !job.entrypoint) {
    console.error("Invalid job data");
    return null;
  }

  // Extract stringified JSON from entrypoint property
  // refer to docs @http://localhost:8000/docs#/health/get_job_metadata_api_v1_health_jobs__job_id__get
  const inputString = job.entrypoint;
  const configString = inputString.split("--config")[1]?.trim();

  if (!configString) {
    console.error("No config found in job entrypoint");
    return null;
  }

  try {
    const jsonObject = JSON.parse(configString.replace(/^'/, '').replace(/'$/, ''));
    jsonObject.dataset = {
      id: jsonObject.dataset.path.match(/datasets\/([^/]+)\/([^/]+)/)?.[1],
      name: jsonObject.dataset.path.match(/datasets\/([^/]+)\/([^/]+)/)?.[2],
    }
    jsonObject.name = jsonObject.name.split('/')[0];

    // Normalize the max_samples
    const jobMax = jsonObject?.job?.max_samples;
    const evalMax = jsonObject?.evaluation?.max_samples;
    if (jobMax === undefined && evalMax !== undefined) {
      (jsonObject.job ??= {}).max_samples = evalMax;
    } else if (jobMax === undefined) {
      throw new Error("Unable to parse max_samples from entrypoint config: " + jsonObject);
    }

    // Normalize the model path
    let modelPath = '';
    if (jsonObject?.model?.path !== undefined) {
      modelPath = jsonObject.model.path;
    } else if (jsonObject?.hf_pipeline?.model_uri !== undefined) {
      modelPath = jsonObject.hf_pipeline.model_uri;
    } else if (jsonObject?.inference_server?.engine !== undefined) {
      modelPath = jsonObject.inference_server.engine;
    } else {
      throw new Error("Unable to parse model path from entrypoint config: " + jsonObject);
    }

    (jsonObject.model ??= {}).path = modelPath;

    return jsonObject;
  } catch (error) {
    console.error("Failed to parse JSON in entrypoint:", error);
    return null;
  }
}

export function calculateDuration(start, finish) {
  // Calculate the time difference in milliseconds
  const differenceInMilliseconds = new Date(finish) - new Date(start);

  if (isNaN(differenceInMilliseconds)) {
    throw new Error("Invalid date format. Please provide valid ISO timestamps.");
  }

  const totalSeconds = Math.floor(differenceInMilliseconds / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  // Format the result as hh:mm:ss
  const duration = `${String(hours).padStart(2, '0')}:
  ${String(minutes).padStart(2, '0')}:
  ${String(seconds).padStart(2, '0')}`;
  return duration;
}

export function downloadContent(blob, filename) {
  const downloadUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.className = 'hidden';
  anchor.href = downloadUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  URL.revokeObjectURL(downloadUrl);
  document.body.removeChild(anchor);
}
