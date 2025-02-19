import type { Experiment } from '@/types/Experiment'
import type { WorkflowResults } from '@/types/Metrics'
import axios from 'axios'
import { transformJobResults } from './transformJobResults'

export async function getExperimentResults(experiment: Experiment) {
  const results = []
  for (const workflow of experiment.workflows) {
    if (workflow.artifacts_download_url) {
      const { data }: { data: WorkflowResults } = await axios.get(workflow.artifacts_download_url)

      const modelRow = {
        model: data.artifacts.model,
        meteor: data.metrics.meteor,
        bertscore: data.metrics.bertscore,
        rouge: data.metrics.rouge,
        runTime: undefined, //getJobRuntime(results.id),
        jobResults: transformJobResults(data),
      }
      results.push(modelRow)
    }
  }
  return results
}
