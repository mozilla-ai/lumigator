import type { EvaluationJobResults } from "@/types/Experiment"
import type { WorkflowResults } from "@/types/Metrics"

/**
 * Transforms results data into a format which accommodates the UI
 *
 * @param {Object} objectData .
 * @returns {Array} Transformed results array.
 */
export function transformJobResults(objectData: WorkflowResults): EvaluationJobResults[] {
  const transformedArray = objectData.artifacts.examples.map((example, index: number) => {
    return {
      example,
      bertscore: {
        f1: objectData.metrics.bertscore?.f1?.[index] ?? 0,
        f1_mean: objectData.metrics.bertscore?.f1_mean ?? 0,
        hashcode: objectData.metrics.bertscore?.hashcode ?? 0,
        precision: objectData.metrics.bertscore?.precision?.[index] ?? 0,
        precision_mean: objectData.metrics.bertscore?.precision_mean ?? 0,
        recall: objectData.metrics.bertscore?.recall?.[index] ?? 0,
        recall_mean: objectData.metrics.bertscore?.recall_mean ?? 0,
      },
      evaluation_time: objectData.artifacts.evaluation_time ?? 0,
      ground_truth: objectData.artifacts.ground_truth?.[index],
      meteor: {
        meteor: objectData.metrics.meteor?.meteor?.[index] ?? 0,
        meteor_mean: objectData.metrics.meteor?.meteor_mean ?? 0,
      },
      model: objectData.artifacts.model,
      predictions: objectData.artifacts.predictions?.[index],
      rouge: {
        rouge1: objectData.metrics.rouge?.rouge1?.[index] ?? 0,
        rouge1_mean: objectData.metrics.rouge?.rouge1_mean ?? 0,
        rouge2: objectData.metrics.rouge?.rouge2?.[index] ?? 0,
        rouge2_mean: objectData.metrics.rouge?.rouge2_mean ?? 0,
        rougeL: objectData.metrics.rouge?.rougeL?.[index] ?? 0,
        rougeL_mean: objectData.metrics.rouge?.rougeL_mean ?? 0,
        rougeLsum: objectData.metrics.rouge?.rougeLsum?.[index] ?? 0,
        rougeLsum_mean: objectData.metrics.rouge?.rougeLsum_mean ?? 0,
      },
      summarization_time: objectData.artifacts.summarization_time,
    } as unknown as EvaluationJobResults
  })
  return transformedArray
}
