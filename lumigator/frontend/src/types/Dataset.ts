export type Dataset = {
  id: string
  filename: string
  format: string
  size: number
  ground_truth: boolean
  run_id: string | null
  generated: boolean
  generated_by: unknown
  created_at: string
}
