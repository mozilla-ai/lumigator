export const PATH_EXPERIMENTS_ROOT = () => `jobs/`;
export const PATH_EXPERIMENT_DETAILS = (experiment_id) => `jobs/${experiment_id}`;
export const PATH_EXPERIMENT_LOGS = (id) => `jobs/${id}/logs`
// these 👆 endopoints do not belong to the experiments API,
// temporary solution until
// migration to "job" API route
