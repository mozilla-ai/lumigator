import ray
from typing import Dict, List
import datasets
from vllm import LLM, SamplingParams
from typing import Dict
import numpy as np
import argparse


# Use a class to initialize the model just once in `__init__`
# and re-use it for inference across multiple batches.
class VllmPredictor:
    def __init__(self):  # , model
        # Create an LLM.
        self.llm = LLM(model="facebook/bart-large-cnn")
        # Create a sampling params object.
        self.sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    # Logic for inference on 1 batch of data.
    def __call__(self, batch: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        # print(batch["dialogue"])
        predictions = self.llm.generate(batch["dialogue"], self.sampling_params)
        prompt: List[str] = []
        generated_text: List[str] = []

        # TODO: Pass in summarization prompt?

        for output in predictions:
            prompt.append(output.prompt)
            generated_text.append(" ".join([o.text for o in output.outputs]))
        return {
            "prompt": prompt,
            "generated_text": generated_text,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name", type=str, required=True
    )  # "facebook/opt-125m" llama2_chat_7B facebook/bart-large-cnn
    parser.add_argument(
        "--dataset_name", type=str, required=True
    )  # "knkarthick/dialogsum"

    # TODO
    # parser.add_argument(
    #    "--results_location", type=str, required=True
    # )

    args = parser.parse_args()

    print(
        f"Now running batch inference on dataset {args.dataset_name} via model {args.model_name} "
    )

    # TODO: add more checks (check if args are empty, etc)

    # TODO: Distinguish between different kinds of datasets
    hf_dataset = datasets.load_dataset(args.dataset_name)
    # TODO: Allow option to pass this in
    ray_ds = ray.data.from_huggingface(hf_dataset["train"])  #

    ray_ds.show(limit=1)

    predictions = ray_ds.limit(10).map_batches(
        VllmPredictor, concurrency=1, num_gpus=1, batch_size=10
    )

    predictions.show(limit=1)

    # TODO: Write results back to s3


if __name__ == "__main__":
    main()
