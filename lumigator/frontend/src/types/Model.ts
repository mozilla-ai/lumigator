export type Model = {
  id: string
  description: string
  info?: ModelInfo
  display_name: string
  requirements: Array<string>
  tasks: Array<Task>
  model: string
  provider: string
  base_url: string
  website_url: string
}

export type ModelInfo = {
  parameter_count: string
  model_size: string
  tensor_type: string
}

export type Task =
  | { summarization: SummarizationTask }
  | { translation: TranslationTask }

export type SummarizationTask = {
  early_stopping?: boolean
  length_penalty?: number
  max_length?: number
  min_length?: number
  no_repeat_ngram_size?: number
  num_beams?: number
}

export type TranslationTask = Record<string, unknown>
