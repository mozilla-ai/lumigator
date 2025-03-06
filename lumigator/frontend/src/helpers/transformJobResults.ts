import type { EvaluationJobResults } from '@/types/Experiment'
import type { WorkflowResults } from '@/types/Metrics'

/**
 * Transforms results data into a format which accommodates the UI
 *
 * @param {Object} objectData .
 * @returns {Array} Transformed results array.
 */
export function transformJobResults(objectData: WorkflowResults): EvaluationJobResults[] {
  const { metrics } = objectData

  const transformedArray = objectData.artifacts.examples.map((example, index: number) => {
    return {
      example,
      bertscore: {
        f1: metrics.bertscore?.f1?.[index] ?? 0,
        f1_mean: metrics.bertscore?.f1_mean ?? 0,
        hashcode: metrics.bertscore?.hashcode ?? 0,
        precision: metrics.bertscore?.precision?.[index] ?? 0,
        precision_mean: metrics.bertscore?.precision_mean ?? 0,
        recall: metrics.bertscore?.recall?.[index] ?? 0,
        recall_mean: metrics.bertscore?.recall_mean ?? 0,
      },
      evaluation_time: objectData.artifacts.evaluation_time ?? 0,
      ground_truth: objectData.artifacts.ground_truth?.[index],
      meteor: {
        meteor: metrics.meteor?.meteor?.[index] ?? 0,
        meteor_mean: metrics.meteor?.meteor_mean ?? 0,
      },
      bleu: {
        bleu: metrics.bleu?.bleu?.[index] ?? 0,
        bleu_mean: metrics.bleu?.bleu_mean ?? 0,
      },
      model: objectData.artifacts.model,
      predictions: objectData.artifacts.predictions?.[index],
      rouge: {
        rouge1: metrics.rouge?.rouge1?.[index] ?? 0,
        rouge1_mean: metrics.rouge?.rouge1_mean ?? 0,
        rouge2: metrics.rouge?.rouge2?.[index] ?? 0,
        rouge2_mean: metrics.rouge?.rouge2_mean ?? 0,
        rougeL: metrics.rouge?.rougeL?.[index] ?? 0,
        rougeL_mean: metrics.rouge?.rougeL_mean ?? 0,
        rougeLsum: metrics.rouge?.rougeLsum?.[index] ?? 0,
        rougeLsum_mean: metrics.rouge?.rougeLsum_mean ?? 0,
      },
      inference_time: objectData.artifacts.inference_time,
    } as unknown as EvaluationJobResults
  })
  return transformedArray
}
