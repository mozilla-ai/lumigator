export const PATH_EXPERIMENTS_ROOT = () => `experiments/`
export const PATH_EXPERIMENTS_EVALUATE = () => `experiments/evaluate/`
export const PATH_EXPERIMENT_DETAILS = (experiment_id) => `health/jobs/${experiment_id}`
// this 👆 endopoint does not belong to the experinments API, it's a temporary until
// migration to "job" API route
