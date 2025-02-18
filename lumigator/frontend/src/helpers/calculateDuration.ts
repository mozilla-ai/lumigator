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
