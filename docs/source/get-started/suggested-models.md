# Suggested Models

Users can carry out evaluation experiments currently for two tasks with Lumigator: *summarization* and *translation*.
Lumigator supports evaluation with range of models for these tasks - including API-based models (e.g., OpenAI's GPT-4o)
and LLMs [hosted on-premise or on cloud](https://blog.mozilla.ai/running-an-open-source-llm-in-2025/) as well as models from Hugging Face Model Hub (e.g., BART for summarization). Please refer to the [local model guide](../user-guides/local-models.md) for evaluation of local models available via providers such as Ollama and the [remote deployment guide](../operations-guide/vllm-rayserve-deployment.md) for evaluation of models deployed on remote servers via vLLM and Ray Serve.

It is recommended to check if the model is compatible with the required library versions
(e.g., Transformers) and runtime dependencies (e.g., vLLM). Practical factors such as compute
availability and system configurations may also impact the successful use of a model. To get
started, [we have extensively tested a few models](https://blog.mozilla.ai/on-model-selection-for-text-summarization/)
and created an endpoint to easily retrieve them.

```{note}
**Using Hugging Face Models**:
For *summarization*, Lumigator supports any summarization model uploaded to the [HF Model Hub](https://huggingface.co/models?pipeline_tag=summarization&sort=trending). For *translation*, current support is limited to model families based on [translation-prefix](https://huggingface.co/bigscience/mt0-base) (e.g., `bigscience/mt0-base`) and those based on [language code specification](https://huggingface.co/facebook/m2m100_418M) in the generation pipeline (e.g., `facebook/m2m100_418M`). Please check the supported models {{ '[here](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/jobs/inference/model_clients/translation_models.yaml)'.format(commit_id) }}.
```

In this guide, we assume that you have already [installed Lumigator locally](quickstart), and have a
running instance. To get a list of suggested models, you can use the following command specifying the task name (`summarization` or `translation`):

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

```console
user@host:~/lumigator$ export TASK="summarization"
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/models/?tasks=$TASK | jq
{
  "total": 7,
  "items": [
    {
      "name": "facebook/bart-large-cnn",
      "model": "facebook/bart-large-cnn",
      "provider": "hf",
      "description": "BART is a large-sized model fine-tuned on the CNN Daily Mail dataset.",
      "info": {
        "parameter_count": "406M",
        "tensor_type": "F32",
        "model_size": "1.63GB"
      },
      "tasks": [
        {
          "summarization": {
...
```

:::

:::{tab-item} Python SDK
:sync: tab2
```python
from lumigator_sdk.lumigator import LumigatorClient

# The default port for Lumigator is 8000
task = "summarization"
lm_client = LumigatorClient("localhost:8000")
lm_client.models.get_suggested_models([task])
```
:::

::::

```{note}
Note that the default port for Lumigator is `8000`. If you are running Lumigator on a different
port, you should replace `8000` with the correct port number.
```

The output will show a list of suggested models we have tested. The `uri` field is the one you
should use when creating a new evaluation job. The response also includes other useful information,
such the model size and the default parameters used for evaluation. These fields are not applicable
to every model, but they are included for the ones we have tested.

```{note}
These are the models we recommend users try for specific tasks, meaning they are suggested for
evaluation on user-provided datasets. Note that Lumigator may also use additional models indirectly
during evaluation, through third-party libraries it uses. For instance, calculating the BERTScore
metric requires the [`roberta-large`](https://huggingface.co/FacebookAI/roberta-large) model by
default. While this model is not listed among the recommended ones, it is still used under the hood.
```

## Model Types and Parameters

The following table shows the models we have tested and their respective types.
The `HuggingFace` column shows if the model is on the Hugging Face Hub, `API` indicates availability
via an external API, and `llamafile` shows if it is distributed as a
[llamafile](https://github.com/Mozilla-Ocho/llamafile).

```{note}
Please note we do not, at present, launch a llamafile for you, Lumigator assumes you have already
launched it.
```

**Summarization-Specific Models**

| **Model Type** | **Model**                              | **HuggingFace** | **API** | **llamafile** |
|----------------|---------------------------------------|-----------------|---------|---------------|
| seq2seq        | facebook/bart-large-cnn              | X               |         |               |
| seq2seq        | Falconsai/text_summarization         | X               |         |               |

**Translation-Specific Models**

| **Model Type** | **Model**                              | **HuggingFace** | **API** | **llamafile** |
|----------------|---------------------------------------|-----------------|---------|---------------|
| seq2seq        | facebook/m2m100_418M,<br>facebook/m2m100_1.2B              | X               |         |               |
| seq2seq        | bigscience/mt0-base,<br>bigscience/mt0-large,<br>bigscience/mt0-xl              | X               |         |               |

**Task-Agnostic Models**:
These models can be used for either summarization or translation by changing the instructions in the prompt.

| **Model Type** | **Model**                              | **HuggingFace** | **API** | **llamafile** |
|----------------|---------------------------------------|-----------------|---------|---------------|
| causal         | gpt-4o-mini, gpt-4o                  |                 | X       |               |
| causal         | deepseek-V3, deepseek-R1             |                 | X       |               |
| causal         | Ministral-8B                         |                 | X       |               |
| causal         | Mistral-7B-Instruct                  |                 |         | X             |


### BART Large CNN

The [`facebook/bart-large-cnn`](https://huggingface.co/facebook/bart-large-cnn) model is pre-trained
on English language, and fine-tuned on [CNN Daily Mail](https://huggingface.co/datasets/cnn_dailymail).
It was introduced in the paper
[BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension](https://arxiv.org/abs/1910.13461)
by Lewis et al. and first released [here](https://github.com/pytorch/fairseq/tree/master/examples/bart).

The model has 406M parameters (FP32), and the model size is 1.63GB. The default parameters used for
evaluation are:

| Parameter Name         | Description                                            | Value |
|------------------------|--------------------------------------------------------|-------|
| `max_length`           | Maximum length of the summary                          | 142   |
| `min_length`           | Minimum length of the summary                          | 56    |
| `length_penalty`       | Length penalty to apply during beam search             | 2.0   |
| `early_stopping`       | Controls the stopping condition for beam-based methods | true  |
| `no_repeat_ngram_size` | All n-grams of that size can only occur once           | 3     |
| `num_beams`            | Number of beams for beam search                        | 4     |

### Falconsai Text Summarization

The [`Falconsai/text_summarization`](https://huggingface.co/Falconsai/text_summarization) model is
a variant of the T5 transformer model, designed for the task of text summarization. It is adapted
and fine-tuned to generate concise and coherent summaries of input text.

The model has 60.5M parameters (FP32), and the model size is 242MB. The default parameters used for
evaluation are:

| Parameter Name         | Description                                            | Value |
|------------------------|--------------------------------------------------------|-------|
| `max_length`           | Maximum length of the summary                          | 200   |
| `min_length`           | Minimum length of the summary                          | 30    |
| `length_penalty`       | Length penalty to apply during beam search             | 2.0   |
| `early_stopping`       | Controls the stopping condition for beam-based methods | true  |
| `no_repeat_ngram_size` | All n-grams of that size can only occur once           | 3     |
| `num_beams`            | Number of beams for beam search                        | 4     |

### Facebook M2M100

M2M100 is a multilingual encoder-decoder (seq-to-seq) model trained for many-to-many multilingual translation between 100 languages. It was introduced in the paper: [Beyond English-Centric Multilingual Machine Translation](https://arxiv.org/abs/2010.11125).

At inference time, the model works based on language codes (`src_lang` and `tgt_lang`) specified in the HF generation pipeline. There are two variants of the model: `facebook/m2m100_418M` and `facebook/m2m100_1.2B` which differ in the number of parameters. Please check the HF model card for exact list of supported languages.

### BigScience MT0

MT0 is a family of multilingual text-to-text transformer models, designed for zero-shot cross-lingual generalization [Paper: [Crosslingual Generalization through Multitask Finetuning](https://arxiv.org/abs/2211.01786)].

These models are fine-tuned versions of Google's MT5 architecture, and at inference time, they work based on prefix instructions such as "Translate English to French: ". The MT0 family includes multiple variants, which differ in size and parameter count, ranging from 300M to 13.9B parameters. Please check the HF model card for exact list of supported languages.

### Mistral 7B Instruct

The [mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)
Large Language Model (LLM) is an instruct fine-tuned version of the
[Mistral-7B-v0.3](https://huggingface.co/mistralai/Mistral-7B-v0.3).

The model has 7.25B parameters (BF16), and the model size is 14.5GB.

### GPT-4o Mini and GPT-4o

The GPT-4o Mini and GPT-4o models are causal language models developed by OpenAI.

There are no summarization-specific parameters for these models.

### Deepseek-V3 and Deepseek-R1
DeepSeek-V3 is a general-purpose LLM with a Mixture-of-Experts (MoE) architecture, featuring 671B parameters (37B activated per token) for NLP tasks like text generation, translation, and summarization. DeepSeek-R1 is a reasoning model built on top of DeepSeek-V3, trained with reinforcement learning for advanced chain-of-thought reasoning and error correction.

### Ministral 8B

The [Ministral 8B](https://mistral.ai/news/ministraux) model is an open, causal language
model developed by [Mistral AI](https://mistral.ai/). It is a small but powerful edge model.

### Mistral 7B Instruct Llamafile

The [mistralai/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
model is a causal language model developed by [Mistral AI](https://mistral.ai/), packaged as a
llamafile. A llamafile is an executable LLM that you can run on your own computer. It contains the
weights for a given open LLM, as well as everything needed to actually run that model on your
computer. There's nothing to install or configure.

## Reference Models

Before you jump into evaluating datasets, you should consider the following importance of quality ground-truth and annotations.

Ground-truth would be the actual, expected output or correct answer in for a given task (such as summarization), serving as a reference to compare the model's predictions. Typically, a human with enough expertise in the task will annotate or label a dataset with those references for each sample (for example, an acceptable summary of the input text).

To evaluate a model as reliably as possible, we encourage using human-provided ground-truth to compare against. Failing that, Lumigator enables the user to do automatic annotation with a [well tested model](https://blog.mozilla.ai/on-model-selection-for-text-summarization/) ([BART](https://mozilla-ai.github.io/lumigator/get-started/suggested-models.html#bart-large-cnn) for summarization task). Automatic annotation for translation task is currently not supported.

You can do this through the API, using one of Lumigator jobs: `/jobs/annotate`.

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

```console
user@host:~/lumigator$
curl -X 'POST' \
  'http://localhost:8000/api/v1/jobs/annotate/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "test_annotate",
  "description": "annotate",
  "dataset": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "max_samples": -1,
  "task": "summarization"
}'
```
Under the hood, this will launch an inference job with the reference model for summarization (BART, described above).
