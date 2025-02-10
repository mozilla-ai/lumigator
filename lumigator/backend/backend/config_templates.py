# Evaluation templates
from lumigator_schemas.jobs import JobType

# TODO: this default evaluation template should serve for most purposes
#       after we deprecate evaluator, as it won't include predictions (model
#       name is just passed for reference and not for actual inference).
#       We can remove all the above templates then.
default_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_uri}" }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}"
    }}
}}"""


# Inference templates

default_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "dataset": {{ "path": "{dataset_path}" }},
    "hf_pipeline": {{
        "model_uri": "{model_uri}",
        "task": "{task}",
        "accelerator": "{accelerator}",
        "revision": "{revision}",
        "use_fast": "{use_fast}",
        "trust_remote_code": "{trust_remote_code}",
        "torch_dtype": "{torch_dtype}",
        "max_new_tokens": "{max_new_tokens}"
    }},
     "job": {{
        "max_samples": {max_samples},
        "storage_path": "{storage_path}",
        "output_field": "{output_field}"
    }}
}}"""

seq2seq_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_uri}" }},
    "dataset": {{ "path": "{dataset_path}" }}
}}"""

bart_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "dataset": {{ "path": "{dataset_path}" }},
    "hf_pipeline": {{
        "model_uri": "{model_uri}",
        "task": "{task}",
        "accelerator": "{accelerator}",
        "revision": "{revision}",
        "use_fast": "{use_fast}",
        "trust_remote_code": "{trust_remote_code}",
        "torch_dtype": "{torch_dtype}",
        "max_new_tokens": 142
    }},
     "job": {{
        "max_samples": {max_samples},
        "storage_path": "{storage_path}",
        "output_field": "{output_field}"
    }}
}}"""

causal_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_uri}" }},
    "dataset": {{ "path": "{dataset_path}" }}
}}"""


oai_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "dataset": {{ "path": "{dataset_path}" }},
    "job": {{
        "max_samples": {max_samples},
        "storage_path": "{storage_path}",
        "output_field": "{output_field}"
    }},
    "inference_server": {{
        "base_url": "{model_url}",
        "engine": "{model_uri}",
        "system_prompt": "{system_prompt}",
        "max_retries": 3
    }},
    "params": {{
        "max_tokens": {max_tokens},
        "frequency_penalty": {frequency_penalty},
        "temperature": {temperature},
        "top_p": {top_p}
    }}
}}"""


templates = {
    JobType.INFERENCE: {
        "default": default_infer_template,
        "hf://facebook/bart-large-cnn": bart_infer_template,
        "oai://gpt-4o-mini": oai_infer_template,
        "oai://gpt-4o": oai_infer_template,
        "mistral://open-mistral-7b": oai_infer_template,
        "llamafile://mistralai/Mistral-7B-Instruct-v0.2": oai_infer_template,
    },
    # TODO: Remove the old EVALUATION section and rename EVALUATION_LITE
    #       to EVALUATION after we deprecate evaluator. Also remove the
    #       unused templates above (all the eval templates except default)
    JobType.EVALUATION_LITE: {
        "default": default_eval_template,
    },
}
