import type { Experiment } from '@/types/Experiment'
import type { WorkflowResults } from '@/types/Metrics'
import axios from 'axios'

export async function getExperimentResults(
  experiment: Experiment,
): Promise<TableDataForExperimentResults[]> {
  const results = []
  for (const workflow of experiment.workflows) {
    if (workflow.artifacts_download_url) {
      const { data }: { data: WorkflowResults } = await axios.get(workflow.artifacts_download_url)

      const modelRow = transformExperimentResults(data)
      results.push(modelRow)
    }
  }
  return results
}

export type TableDataForExperimentResults = {
  model: string
  'Bert P': string
  Meteor: string
  'Bert R': string
  'Bert F1': string
  'Rouge-1': string
  'Rouge-2': string
  'ROUGE-L': string
  bleu: string
  runTime: string | undefined
  subRows: TableDataForWorkflowResults[]
}

function transformExperimentResults(objectData: WorkflowResults): TableDataForExperimentResults {
  const data = objectData

  return {
    model: data.artifacts.model,
    'Bert P': data.metrics.bertscore.precision_mean.toFixed(2),
    Meteor: data.metrics.meteor.meteor_mean.toFixed(2),
    'Bert R': data.metrics.bertscore.recall_mean.toFixed(2),
    'Bert F1': data.metrics.bertscore.f1_mean.toFixed(2),
    'Rouge-1': data.metrics.rouge.rouge1_mean.toFixed(2),
    'Rouge-2': data.metrics.rouge.rouge2_mean.toFixed(2),
    'ROUGE-L': data.metrics.rouge.rougeL_mean.toFixed(2),
    bleu: data.metrics.bleu.bleu_mean.toFixed(2),
    // 'model size': data.artifacts.model.info?.model_size.replace(/(\d+(?:\.\d+)?)([a-zA-Z]+)/g, '$1 $2')
    // 'parameters':  data.artifacts.model.info?.parameter_count.replace(
    //       /(\d+(?:\.\d+)?)([a-zA-Z]+)/g,
    //       '$1 $2',
    //     )
    runTime: undefined, //getJobRuntime(results.id),
    subRows: transformWorkflowResults(data),
  }
}

export type TableDataForWorkflowResults = {
  Examples: string
  'Ground Truth': string
  predictions: string
  'rouge-1': string
  'rouge-2': string
  'rouge-L': string
  meteor: string
  'bert-p': string
  'bert-f1': string
  bleu: string
  evaluation_time: string
  inference_time: string
}

/**
 * Transforms results data into a format which accommodates the UI
 *
 * @param {Object} objectData .
 * @returns {Array} Transformed results array.
 */
export function transformWorkflowResults(
  objectData: WorkflowResults,
): TableDataForWorkflowResults[] {
  return objectData.artifacts.examples.map((example, index: number) => {
    return {
      rowNumber: index + 1,
      Examples: example,
      'Ground Truth': objectData.artifacts.ground_truth?.[index],
      predictions: objectData.artifacts.predictions?.[index],
      'rouge-1': objectData.metrics.rouge?.rouge1?.[index].toFixed(2) ?? 0,
      'rouge-2': objectData.metrics.rouge?.rouge2?.[index].toFixed(2) ?? 0,
      'rouge-L': objectData.metrics.rouge?.rougeL?.[index].toFixed(2) ?? 0,
      meteor: objectData.metrics.meteor?.meteor?.[index].toFixed(2) ?? 0,
      'bert-p': objectData.metrics.bertscore?.precision?.[index].toFixed(2) ?? 0,
      'bert-f1': objectData.metrics.bertscore?.f1?.[index].toFixed(2) ?? 0,
      bleu: objectData.metrics.bleu?.bleu?.[index].toFixed(2) ?? 0,
      // bert_recall: objectData.metrics.bertscore?.recall?.[index].toFixed(2) ?? 0,
      evaluation_time: objectData.artifacts.evaluation_time.toFixed(2) ?? 0,
      // meteor_mean: objectData.metrics.meteor?.meteor_mean.toFixed(2) ?? 0,
      // bleu_mean: objectData.metrics.bleu?.bleu_mean.toFixed(2) ?? 0,
      // model: objectData.artifacts.model,
      // rouge1_mean: objectData.metrics.rouge?.rouge1_mean.toFixed(2) ?? 0,
      // rouge2_mean: objectData.metrics.rouge?.rouge2_mean.toFixed(2) ?? 0,
      // rougeL_mean: objectData.metrics.rouge?.rougeL_mean.toFixed(2) ?? 0,
      // rougeLsum: objectData.metrics.rouge?.rougeLsum?.[index].toFixed(2) ?? 0,
      // rougeLsum_mean: objectData.metrics.rouge?.rougeLsum_mean.toFixed(2) ?? 0,
      inference_time: objectData.artifacts.inference_time.toFixed(2) ?? 0,
    }
  })
}
