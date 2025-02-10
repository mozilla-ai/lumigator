# Evaluation templates
from lumigator_schemas.jobs import JobType

seq2seq_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_uri}" }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "use_pipeline": true,
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}",
        "skip_inference": "{skip_inference}"
    }}
}}"""

bart_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_uri}" }},
    "tokenizer": {{ "path": "{model_uri}", "mod_max_length": 1024 }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "use_pipeline": true,
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}",
        "skip_inference": "{skip_inference}"
    }}
}}"""

causal_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_uri}" }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "use_pipeline": false,
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}",
        "skip_inference": "{skip_inference}"
    }}
}}"""

oai_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{
        "inference": {{
            "base_url": "{model_url}",
            "engine": "{model_uri}",
            "system_prompt": "{system_prompt}",
            "max_retries": 3
        }}
    }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}",
        "skip_inference": "{skip_inference}"
    }}
}}"""

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


# Theoretically many more models and providers could be supported here
# See https://docs.litellm.ai/docs/providers for a list of supported providers
supported_litellm_providers_models = [
    # GPT Models
    "gpt-4o-mini",
    "gpt-4o",
    "o1",
    "o3-mini",
    # Mistral Models
    "mistral/open-mistral-7b",
    "mistral/open-mixtral-8x7b",
    "mistral/open-mixtral-8x22b",
    "mistral/mistral-large-latest",
    "mistral/open-mistral-nemo",
    # Deepseek
    "deepseek/deepseek-reasoner",
    "deepseek/deepseek-chat",
]

templates = {
    JobType.INFERENCE: {
        "default": default_infer_template,
        **{endpoint: oai_infer_template for endpoint in supported_litellm_providers_models},
        "hf://facebook/bart-large-cnn": bart_infer_template,
        "llamafile://mistralai/Mistral-7B-Instruct-v0.2": oai_infer_template,
    },
    JobType.EVALUATION: {
        "default": causal_eval_template,
        "hf://facebook/bart-large-cnn": bart_eval_template,
        "hf://Falconsai/text_summarization": seq2seq_eval_template,
        "hf://mistralai/Mistral-7B-Instruct-v0.3": causal_eval_template,
        "oai://gpt-4o-mini": oai_eval_template,
        "oai://gpt-4o": oai_eval_template,
        "mistral://open-mistral-7b": oai_eval_template,
        "llamafile://mistralai/Mistral-7B-Instruct-v0.2": oai_eval_template,
    },
    # TODO: Remove the old EVALUATION section and rename EVALUATION_LITE
    #       to EVALUATION after we deprecate evaluator. Also remove the
    #       unused templates above (all the eval templates except default)
    JobType.EVALUATION_LITE: {
        "default": default_eval_template,
    },
}
