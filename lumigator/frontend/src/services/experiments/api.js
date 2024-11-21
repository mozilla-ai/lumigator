export const PATH_EXPERIMENTS_EVALUATE = () => `experiments/evaluate/`
export const PATH_EXPERIMENTS_ROOT = () => `health/jobs/`;
export const PATH_EXPERIMENT_DETAILS = (experiment_id) => `health/jobs/${experiment_id}`;
export const PATH_EXPERIMENT_RESULTS = (job_id) => `experiments/${job_id}/result/download`
// these 👆 endopoints do not belong to the experiments API,
// temporary solution until
// migration to "job" API route
