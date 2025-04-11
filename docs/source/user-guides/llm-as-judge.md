# Running LLM-as-judge evaluation

Lumigator relies on [Deepeval's G-Eval implementation](https://docs.confident-ai.com/docs/metrics-llm-evals)
to run LLM-as-judge evaluations of models used for summarization and translation tasks. From the user's point
of view, these look like just other evaluation metrics that can be specified via API call.

```{note}
At the present time LLM-as-judge metrics are only available via API, but we are planning to make them available in the UI soon. As soon as they are, you'll be able to add them to your evaluations just as any other metric.
```

By default, [DeepEval uses gpt-4o](https://docs.confident-ai.com/integrations/model-openai) to power all of
its evaluation metrics. It is however possible to use self-hosted models as an alternative, and we'll show
you how in this guide.

## Available metrics

The LLM-as-judge evaluation metrics implemented in Lumigator are inspired by the paper
"[G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634)"
(reference code [here](https://github.com/nlpyang/geval/tree/main)). For each task (e.g. summarization,
translation) Lumigator provides different to evaluate across different dimensions. In particular:

- `g_eval_summarization`: this metric uses an original sample and a reference summary to evaluate
a newly generated summary across the following dimensions: `coherence`, `consistency`, `fluency`, `relevance`
(see reference g-eval prompts [here](https://github.com/nlpyang/geval/tree/main/prompts/summeval) for
comparison).

- `g_eval_translation`: this metric uses an original sample and a reference translation to evaluate
a newly generated translation across the following dimensions: `consistency`, `fluency`.

- `g_eval_translation_noref`: this metric runs an evaluation across the same dimensions of the previous one,
but explicitly ignoring the reference translation (helpful in case you don't have ground truth available).

When you choose any of the above metrics, Lumigator will prompt an external LLM (either OpenAI's
or self-hosted) to evaluate your model's predictions across all the dimensions that are predefined
for the specified task. These dimensions, as well as the prompts that are used for them, are specified
{{ '[in this JSON file](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/jobs/evaluator/g_eval_prompts.json)'.format(commit_id) }}.

## Running LLM-as-judge with gpt-4o

Assuming you have already run inference on a given dataset and you have recovered its id (you can do that by clicking on the dataset row in the Web UI and then choosing `Copy ID` in the right pane), running LLM-as-judge evaluation boils down to specifying the corresponding g_eval metric for your task (or adding it to any other metric you'd like to calculate). For instance, for translation:

::::{tab-set}

:::{tab-item} cURL
:sync: tab1
```console
user@host:~/lumigator$ curl -X 'POST' \
  'http://localhost:8000/api/v1/jobs/evaluator/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "llm-as-judge translation eval",
  "description": "",
  "dataset": "<paste your dataset id here>",
  "max_samples": -1,
  "job_config": {
    "secret_key_name": "openai_api_key",
    "job_type": "evaluator",
    "metrics": [
      "blue",
      "g_eval_translation"
    ]
  }
}'
```
:::

::::

```{note}
If you use OpenAI models you will have to first configure your API keys in the Lumigator UI (under [Settings](https://mozilla-ai.github.io/lumigator/operations-guide/configuration.html#api-settings)) and specify `openai_api_key` as your job's `secret_key_name` parameter.
```

## Running LLM-as-judge with Ollama

You can run LLM-as-judge with Ollama by simply specifying the metric you want to calculate, the Ollama server URL, and the name of the model you want to hit. For instance, for summarization:


::::{tab-set}

:::{tab-item} cURL
:sync: tab1
```console
user@host:~/lumigator$ curl -X 'POST' \
  'http://localhost:8000/api/v1/jobs/evaluator/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "llm-as-judge summarization eval",
  "description": "",
  "dataset": "<paste your dataset id here>",
  "max_samples": -1,
  "job_config": {
    "job_type": "evaluator",
    "metrics": [
      "bertscore",
      "g_eval_summarization"
    ],
    "llm_as_judge": {
      "model_name": "gemma3:27b",
      "model_base_url": "http://localhost:11434"
    }
  }
}'
```
:::

::::

```{note}
If you want to use a local model for LLM-as-judge, first make sure it has the capabilities to perform the task appropriately (in particular, the model needs to have multilingual capabilities to properly evaluate translations). For instance, the quantized version of gemma3:27b running on Ollama can be a good starting point for both summarization and translation.
```
