export function constructCSVFromJSON(
  json: Record<any, any>,
  columns: string[],
  separator = ',',
): string {
  const header = columns.join(separator) + '\n'

  let body = ''
  if (Array.isArray(json)) {
    body = json.reduce((accum, result) => accum + createRowFromJSON(columns, result, separator), '')
  } else {
    body = createRowFromJSON(columns, json, separator)
  }
  return header + body
}

function createRowFromJSON(columns: string[], json: Record<any, any>, separator = ','): string {
  return columns.map((key) => json[key]).join(separator) + '\n'
}

export function constructJSONFromCSV(csv: string, separator = ','): Record<any, any>[] {
  const rows = csv.split('\n').map((row) => row.trim())
  const columns = rows[0].split(separator)

  const body = rows.slice(1, rows.length)
  return body.map((row) => createJSONFromRow(columns, row, separator))
}

function createJSONFromRow(
  columns: string[],
  row: string,
  separator = ',',
  quoteChar = '"',
): Record<any, any> {
  // sometimes the row can have `""` inside which breaks splitting by comma
  const regex = new RegExp(`\\s*(${quoteChar})?(.*?)\\1\\s*(?:${separator}|$)`, 'gs')
  const values = row.match(regex)?.filter(Boolean) || []

  return values
    .map((value, index) => {
      return {
        [columns[index]]: value,
      }
    })
    .reduce((accum, item) => ({ ...accum, ...item }), {})
}
