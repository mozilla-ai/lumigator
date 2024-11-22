export const PATH_EXPERIMENTS_ROOT = () => `health/jobs/`;
export const PATH_EXPERIMENT_DETAILS = (experiment_id) => `health/jobs/${experiment_id}`;
// these 👆 endopoints do not belong to the experiments API,
// temporary solution until
// migration to "job" API route
export const PATH_EXPERIMENT_RESULTS = (job_id) => `jobs/${job_id}/result/download`
export const PATH_EXPERIMENTS_EVALUATE = () => `jobs/evaluate/`
