import type { Workflow } from './Workflow'

export type ExperimentNew = {
  id: string
  name: string
  created_at: string
  workflows: Workflow[]
}
