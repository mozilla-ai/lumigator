# Evaluator Documentation

`Evaluator` is a collection of jobs for finetuning and evaluating open-source (large) language models, originating with [lm-buddy.](https://github.com/mozilla-ai/lm-buddy)  
The library makes use of YAML-based configuration files as inputs to CLI commands for each job, and tracks input/output artifacts on Weights & Biases.
It's the main entrypoint into evaluation from Lumigator. 

The package currently exposes an evaluation job using HuggingFace `evaluate` or EleutherAI's  `lm-evaluation-harness` with inference performed via an in-process HuggingFace model or an externally-hosted vLLM server.

Evaluator's commands are intended to be used as the entrypoints for jobs on a Ray compute cluster. 
The suggested method for submitting an evaluator job to Ray is by using the Ray Python SDK within a local Python driver script. 
The ultimate configuration passed to Ray via the Lumigator web API within the `experiments` service `create_experiment` [method](https://github.com/mozilla-ai/lumigator/blob/ddf40ee48fe0ab64ec36918844cfcfd26753b753/lumigator/python/mzai/backend/services/experiments.py#L73) follows this Ray pattern:

```python
from ray.job_submission import JobSubmissionClient

runtime_env = {
            "pip": settings.PIP_REQS, #evaluator-specific requirements
            "working_dir": "./",
            "env_vars": runtime_env_vars,
        }

def command(self) -> str:
        # evaluator passed as a module to Ray using a JSON-serialized config.
        return (
            f"python -m entrypoint evaluate huggingface"
            f"--config '{json.dumps(self.config.args)}'"
        )

```
and are populated from [these config templates.](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/backend/config_templates.py)
Via [submission run here](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/backend/ray_submit/submission.py). 

