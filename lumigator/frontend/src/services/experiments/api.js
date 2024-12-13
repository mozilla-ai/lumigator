export const PATH_EXPERIMENTS_ROOT = () => `jobs/`;
export const PATH_EXPERIMENT_DETAILS = (experiment_id) => `jobs/${experiment_id}`;
export const PATH_EXPERIMENT_LOGS = (id) => `health/jobs/${id}/logs`
// these 👆 endopoints do not belong to the experiments API,
// temporary solution until
// migration to "job" API route
export const PATH_EXPERIMENT_RESULTS = (job_id) => `experiments/${job_id}/result/download`
export const PATH_EXPERIMENTS_EVALUATE = () => `experiments`
