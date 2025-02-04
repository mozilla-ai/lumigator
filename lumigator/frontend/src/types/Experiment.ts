export type Experiment = {
 id: string;
 created: string;
 dataset: unknown;
  description: string;
  name: string;
  experimentStart: string;
  jobs: Job[];
  useCase: string;
  runTime: string;
  samples: number;
  models: Model[];
  max_samples: number;
  status: string;
}

export type Job = {
  id: string;
  status: string;
  metadata: Record<string, unknown>;
  end_time: string;
  model: Record<string, unknown>;
  name: string;
  experimentStart: string;
}

export type Model = {
  id: string;
  description: string;
  info?: {
    parameter_count: string;
    model_size: string;
    tensor_type: string;
  }
  name: string;
  requirements: Array<string>;
  tasks: Array<Task>;
  uri: string;
  website_url: string;
}

export type Task = {
  summarization: {
    early_stopping: boolean;
    length_penalty: number;
    max_length: number;
    min_length: number;
    no_repeat_ngram_size: number;
    num_beats: number;
  } | null;
}


export type ExperimentResults = {
    model: string;
    meteor: unknown;
    bertscore: unknown;
    rouge: unknown;
    runTime: string | null;
    jobResults: unknown;
}
