# Evaluation templates
seq2seq_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_path}" }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "use_pipeline": true,
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}"
    }}
}}"""

bart_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_path}" }},
    "tokenizer": {{ "path": "{model_path}", "mod_max_length": 1024 }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "use_pipeline": true,
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}"
    }}
}}"""

causal_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_path}" }},
    "dataset": {{ "path": "{dataset_path}" }},
    "evaluation": {{
        "metrics": ["rouge", "meteor", "bertscore"],
        "use_pipeline": false,
        "max_samples": {max_samples},
        "return_input_data": true,
        "return_predictions": true,
        "storage_path": "{storage_path}"
    }}
}}"""

oai_eval_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{
        "inference": {{
            "base_url": "{model_url}",
            "engine": "{model_path}",
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
        "storage_path": "{storage_path}"
    }}
}}"""

# Inference templates

seq2seq_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_path}" }},
    "dataset": {{ "path": "{dataset_path}" }},
}}"""

bart_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_path}" }},
    "tokenizer": {{ "path": "{model_path}", "mod_max_length": 1024 }},
    "dataset": {{ "path": "{dataset_path}" }},
}}"""

causal_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_path}" }},
    "dataset": {{ "path": "{dataset_path}" }},
}}"""

oai_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{
        "inference": {{
            "base_url": "{model_url}",
            "engine": "{model_path}",
            "system_prompt": "{system_prompt}",
            "max_retries": 3
        }}
    }},
    "dataset": {{ "path": "{dataset_path}" }},
}}"""

config_infer_template = {
    "hf://facebook/bart-large-cnn": bart_eval_template,
    "hf://mikeadimech/longformer-qmsum-meeting-summarization": seq2seq_eval_template,
    "hf://mrm8488/t5-base-finetuned-summarize-news": seq2seq_eval_template,
    "hf://Falconsai/text_summarization": seq2seq_eval_template,
    "hf://mistralai/Mistral-7B-Instruct-v0.3": causal_eval_template,
    "oai://gpt-4o-mini": oai_eval_template,
    "oai://gpt-4-turbo": oai_eval_template,
    "oai://gpt-3.5-turbo-0125": oai_eval_template,
    "mistral://open-mistral-7b": oai_eval_template,
    "llamafile://mistralai/Mistral-7B-Instruct-v0.2": oai_eval_template,
}


config_eval_template = {
    "hf://facebook/bart-large-cnn": bart_eval_template,
    "hf://mikeadimech/longformer-qmsum-meeting-summarization": seq2seq_eval_template,
    "hf://mrm8488/t5-base-finetuned-summarize-news": seq2seq_eval_template,
    "hf://Falconsai/text_summarization": seq2seq_eval_template,
    "hf://mistralai/Mistral-7B-Instruct-v0.3": causal_eval_template,
    "oai://gpt-4o-mini": oai_eval_template,
    "oai://gpt-4-turbo": oai_eval_template,
    "oai://gpt-3.5-turbo-0125": oai_eval_template,
    "mistral://open-mistral-7b": oai_eval_template,
    "llamafile://mistralai/Mistral-7B-Instruct-v0.2": oai_eval_template,
}
