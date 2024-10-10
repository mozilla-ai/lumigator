"""Main entrypoint to the Evaluator CLI.

Makes the Evaluator CLI executable via `python -m evaluator`.
"""
from vllm import LLM, SamplingParams
import ray

@ray.remote
class vLLM():

    prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
    ]
    # Create a sampling params object.
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    # Create an LLM.
    llm = LLM(model="facebook/opt-125m")

    outputs = llm.generate(prompts, sampling_params)

    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")


if __name__ == "__main__":
   vllm = vLLM().remote
   ray.get(vllm)





