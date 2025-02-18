import type { Task } from './Experiment'

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
  base_url: string
  website_url: string
}
