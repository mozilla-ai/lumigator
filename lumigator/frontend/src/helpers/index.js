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

  const inputString = job.entrypoint;
  const configString = inputString.split("--config")[1]?.trim();

  if (!configString) {
    console.error("No config found in job entrypoint");
    return null;
  }

  try {
    const jsonObject = JSON.parse(configString.replace(/^'/, '').replace(/'$/, ''));
    jsonObject.dataset = jsonObject.dataset.path.match(/datasets\/([^/]+)/)?.[1];
    jsonObject.name = jsonObject.name.split('/')[0];
    return jsonObject;
  } catch (error) {
    console.error("Failed to parse JSON in entrypoint:", error);
    return null;
  }
}
