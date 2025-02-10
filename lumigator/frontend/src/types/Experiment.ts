export type Experiment = {
  id: string
  created: string
  dataset: unknown
  description: string
  name: string
  experimentStart: string
  jobs: Job[]
  useCase: string
  runTime: string
  samples?: number
  models: Model[]
  max_samples?: number
  status: string
}

export type Job = {
  id: string
  status: string
  metadata: Record<string, unknown>
  end_time: string
  model: Record<string, unknown>
  name: string
  experimentStart: string
  submission_id: string
  start_time: string
  description: string
  entrypoint: string
}

export type Model = {
  id: string
  description: string
  info?: {
    parameter_count: string
    model_size: string
    tensor_type: string
  }
  name: string
  requirements: Array<string>
  tasks: Array<Task>
  uri: string
  website_url: string
}

export type Task = {
  summarization: {
    early_stopping: boolean
    length_penalty: number
    max_length: number
    min_length: number
    no_repeat_ngram_size: number
    num_beats: number
  } | null
}

export type ExperimentResults = {
  model: string
  meteor: Meteor
  bertscore: Bertscore
  rouge: Rouge
  runTime: string | undefined
  jobResults: JobResults
}

export type Bertscore = {
  f1: number[]
  f1_mean: number
  hashcode: number
  precision: number[]
  precision_mean: number
  recall: number[]
  recall_mean: number
}

export type Meteor = {
  meteor: number[]
  meteor_mean: number
}

export type Rouge = {
  rouge1: number[]
  rouge1_mean: number
  rouge2: number[]
  rouge2_mean: number
  rougeL: number[]
  rougeL_mean: number
  rougeLsum: number[]
  rougeLsum_mean: number
}

export type ObjectData = {
  metrics: {
    bertscore?: Bertscore
    meteor?: Meteor
    rouge?: Rouge
    summarization_time: number
    evaluation_time?: number
  }
  artifacts: {
    predictions?: string[]
    ground_truth?: string[]
    model: string
    examples: string[]
  }
}

export type JobResults = {
  example: string
  bertscore: {
    f1: number
    f1_mean: number
    hashcode: number
    precision: number
    precision_mean: number
    recall: number
    recall_mean: number
  }
  evaluation_time: number
  ground_truth?: string
  meteor: {
    meteor: number
    meteor_mean: number
  }
  model: string
  predictions?: string
  rouge: {
    rouge1: number
    rouge1_mean: number
    rouge2: number
    rouge2_mean: number
    rougeL: number
    rougeL_mean: number
    rougeLsum: number
    rougeLsum_mean: number
  }
  summarization_time: number
}
