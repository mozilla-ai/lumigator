# Translation Use Case

This guide will walk you through the process of running a translation experiment using Lumigator with two models: a many-to-many sequence-to-sequence model from the Hugging Face Hub and `gpt-4o-mini` from  OpenAI.

## What You'll Need

1. A running instance of [Lumigator](../get-started/quickstart.md).
1. A dataset for translation use case. You can use the sample [English-Spanish dataset](../../../lumigator/sample_data/translation/sample_translation_en_es.csv) or prepare your own dataset. Refer to [this guide](./prepare-evaluation-dataset.md) for more details.
2. (Optional) An `OPENAI_API_KEY` if you would like to evaluate one of the OpenAI models. Please refer to the [UI instructions](../get-started/ui-guide.html#settings) for setting up the API keys.
