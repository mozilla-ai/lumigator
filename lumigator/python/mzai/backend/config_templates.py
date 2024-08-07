seq2seq_template = """{{
    "name": "{experiment_name}/{experiment_id}",
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

bart_template = """{{
    "name": "{experiment_name}/{experiment_id}",
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

causal_template = """{{
    "name": "{experiment_name}/{experiment_id}",
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

oai_template = """{{
    "name": "{experiment_name}/{experiment_id}",
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

config_template = {
    "hf://facebook/bart-large-cnn": bart_template,
    "hf://mikeadimech/longformer-qmsum-meeting-summarization": seq2seq_template,
    "hf://mrm8488/t5-base-finetuned-summarize-news": seq2seq_template,
    "hf://Falconsai/text_summarization": seq2seq_template,
    "hf://mistralai/Mistral-7B-Instruct-v0.3": causal_template,
    "oai://gpt-4o-mini": oai_template,
    "oai://gpt-4-turbo": oai_template,
    "oai://gpt-3.5-turbo-0125": oai_template,
    "mistral://open-mistral-7b": oai_template,
    "llamafile://mistralai/Mistral-7B-Instruct-v0.2": oai_template,
}
