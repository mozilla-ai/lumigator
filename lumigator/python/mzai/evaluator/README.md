# Evaluator Documentation

`Evaluator` is a collection of jobs for finetuning and evaluating open-source (large) language models, originating with [lm-buddy.](https://github.com/mozilla-ai/lm-buddy)  
The library makes use of YAML-based configuration files as inputs to CLI commands for each job, and tracks input/output artifacts on Weights & Biases.
It's the main entrypoint into evaluation from Lumigator. 

The package currently exposes an evaluation job using HuggingFace `evaluate` or EleutherAI's  `lm-evaluation-harness` with inference performed via an in-process HuggingFace model or an externally-hosted vLLM server.

Evaluator's commands are intended to be used as the entrypoints for jobs on a Ray compute cluster. 
The suggested method for submitting an evaluator job to Ray is by using the Ray Python SDK within a local Python driver script. 
The ultimate configuration passed to Ray via the Lumigator web API within the `experiments` service `create_experiment` method looks like this: 

```python
from ray.job_submission import JobSubmissionClient

client.submit_job(
    entrypoint="lm_buddy finetune <job-name> --config config.yaml", 
    runtime_env=runtime_env,
    entrypoint_num_gpus=1
)
```



