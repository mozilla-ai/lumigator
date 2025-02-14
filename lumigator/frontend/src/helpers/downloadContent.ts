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
