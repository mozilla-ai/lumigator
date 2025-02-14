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
