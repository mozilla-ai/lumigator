import type { Experiment } from '@/types/Experiment'
import type { WorkflowResults } from '@/types/Metrics'
import axios from 'axios'
// import { transformJobResults } from './transformJobResults'

export async function getExperimentResults(experiment: Experiment) {
  const results = []
  for (const workflow of experiment.workflows) {
    if (workflow.artifacts_download_url) {
      const { data }: { data: WorkflowResults } = await axios.get(workflow.artifacts_download_url)

      const modelRow = {
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
        subRows: data.artifacts.examples.map((example, index: number) => {
          return {
            Examples: example,
            'Ground Truth': data.artifacts.ground_truth?.[index],
            predictions: data.artifacts.predictions?.[index],
            'rouge-1': data.metrics.rouge?.rouge1?.[index].toFixed(2) ?? 0,
            'rouge-2': data.metrics.rouge?.rouge2?.[index].toFixed(2) ?? 0,
            'rouge-L': data.metrics.rouge?.rougeL?.[index].toFixed(2) ?? 0,
            meteor: data.metrics.meteor?.meteor?.[index].toFixed(2) ?? 0,
            'bert-p': data.metrics.bertscore?.precision?.[index].toFixed(2) ?? 0,
            'bert-f1': data.metrics.bertscore?.f1?.[index].toFixed(2) ?? 0,
            bleu: data.metrics.bleu?.bleu?.[index].toFixed(2) ?? 0,
            // bert_recall: data.metrics.bertscore?.recall?.[index].toFixed(2) ?? 0,
            evaluation_time: data.artifacts.evaluation_time.toFixed(2) ?? 0,
            // meteor_mean: data.metrics.meteor?.meteor_mean.toFixed(2) ?? 0,
            // bleu_mean: data.metrics.bleu?.bleu_mean.toFixed(2) ?? 0,
            // model: data.artifacts.model,
            // rouge1_mean: data.metrics.rouge?.rouge1_mean.toFixed(2) ?? 0,
            // rouge2_mean: data.metrics.rouge?.rouge2_mean.toFixed(2) ?? 0,
            // rougeL_mean: data.metrics.rouge?.rougeL_mean.toFixed(2) ?? 0,
            // rougeLsum: data.metrics.rouge?.rougeLsum?.[index].toFixed(2) ?? 0,
            // rougeLsum_mean: data.metrics.rouge?.rougeLsum_mean.toFixed(2) ?? 0,
            inference_time: data.artifacts.inference_time.toFixed(2) ?? 0,
          }
        }),
      }
      results.push(modelRow)
    }
  }
  return results
}

// datasetFileContent.value = data
//     .slice(1, data.length)
//     .map((row: string[], rowIndex: number) => {
//       return row.reduce((accum, value, index, array) => {
//         return {
//           ...accum,
//           [columns[index]]: value,
//           rowNumber: rowIndex + 1,
//         }
//       }, {})
//     })
