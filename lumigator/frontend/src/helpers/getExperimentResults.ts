import type { Experiment } from '@/types/Experiment'
import type { WorkflowResults } from '@/types/Metrics'
import type { Model } from '@/types/Model'
import axios from 'axios'

export async function getExperimentResults(
  experiment: Experiment,
  models: Model[],
): Promise<TableDataForExperimentResults[]> {
  const results = []
  for (const workflow of experiment.workflows) {
    if (workflow.artifacts_download_url) {
      const { data }: { data: WorkflowResults } = await axios.get(workflow.artifacts_download_url)

      const modelRow = transformExperimentResults(data, models)
      results.push(modelRow)
    }
  }
  return results
}

export type TableDataForExperimentResults = {
  model: string
  'bert-p'?: string
  Meteor?: string
  Comet?: string
  'bert-r'?: string
  'bert-f1'?: string
  'rouge-1'?: string
  'rouge-2'?: string
  'rouge-l'?: string
  bleu?: string
  // runTime: string | undefined
  subRows: TableDataForWorkflowResults[]
}
export type TableDataForWorkflowResults = {
  Examples: string
  'Ground Truth': string
  predictions: string
  'rouge-1'?: string
  'rouge-2'?: string
  'rouge-l'?: string
  meteor?: string
  comet?: string
  'bert-p'?: string
  'bert-f1'?: string
  bleu?: string
  model_size?: string
  parameters?: string
  // evaluation_time: string
  inference_time: string
}

function transformExperimentResults(
  objectData: WorkflowResults,
  models: Model[],
): TableDataForExperimentResults {
  const data = objectData
  const model = models.find((model) => model.model === data.artifacts.model)

  return {
    model: data.artifacts.model,
    ...(data.metrics.meteor && { Meteor: data.metrics.meteor.meteor_mean.toFixed(2) }),
    ...(data.metrics.bertscore && { 'bert-p': data.metrics.bertscore.precision_mean.toFixed(2) }),
    ...(data.metrics.bertscore && { 'bert-r': data.metrics.bertscore.recall_mean.toFixed(2) }),
    ...(data.metrics.bertscore && { 'bert-f1': data.metrics.bertscore.f1_mean.toFixed(2) }),
    ...(data.metrics.rouge && { 'rouge-1': data.metrics.rouge.rouge1_mean.toFixed(2) }),
    ...(data.metrics.rouge && { 'rouge-2': data.metrics.rouge.rouge2_mean.toFixed(2) }),
    ...(data.metrics.rouge && { 'rouge-l': data.metrics.rouge.rougeL_mean.toFixed(2) }),
    ...(data.metrics.bleu && { bleu: data.metrics.bleu.bleu_mean.toFixed(2) }),
    ...(data.metrics.comet && { Comet: data.metrics.comet.mean_score.toFixed(2) }),
    ...(model &&
      model.info && {
        'model size': model.info.model_size.replace(/(\d+(?:\.\d+)?)([a-zA-Z]+)/g, '$1 $2'),
        parameters: model.info.parameter_count.replace(/(\d+(?:\.\d+)?)([a-zA-Z]+)/g, '$1 $2'),
      }),
    // runTime: undefined, //getJobRuntime(results.id),
    subRows: transformWorkflowResults(data),
  }
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
      ...(objectData.metrics.meteor && {
        meteor: objectData.metrics.meteor.meteor?.[index].toFixed(2),
      }),
      ...(objectData.metrics.bertscore && {
        'bert-p': objectData.metrics.bertscore.precision?.[index].toFixed(2),
      }),
      ...(objectData.metrics.bertscore && {
        'bert-r': objectData.metrics.bertscore.recall?.[index].toFixed(2),
      }),
      ...(objectData.metrics.bertscore && {
        'bert-f1': objectData.metrics.bertscore.f1?.[index].toFixed(2),
      }),
      ...(objectData.metrics.rouge && {
        'rouge-1': objectData.metrics.rouge.rouge1?.[index].toFixed(2),
      }),
      ...(objectData.metrics.rouge && {
        'rouge-2': objectData.metrics.rouge.rouge2?.[index].toFixed(2),
      }),
      ...(objectData.metrics.rouge && {
        'rouge-l': objectData.metrics.rouge.rougeL?.[index].toFixed(2),
      }),
      ...(objectData.metrics.bleu && { bleu: objectData.metrics.bleu.bleu?.[index].toFixed(2) }),
      ...(objectData.metrics.comet && {
        comet: objectData.metrics.comet.scores?.[index].toFixed(2),
      }),
      evaluation_time: String(objectData.artifacts.evaluation_time.toFixed(2) ?? '0'),
      inference_time: String(objectData.artifacts.inference_time.toFixed(2) ?? '0'),
    }
  })
}
