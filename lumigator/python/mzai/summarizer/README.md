# Ray Serve Summarizer

Ray Serve is an inference server for online serving of large language models. In plain English, it’s the software we need stand up in order to send text to an LLM and receive a response. The software takes care of a number of considerations such as: what if two people send a request at at the same time? How to load the model? How can we monitor the memory size of both the model and the K-V cache?

## Why Ray Serve?

We’ve generally had two fundamental needs from large language models:
the ability to try them ad-hoc and evaluate based on model “vibes”, and
the ability to systematically perform batch model inference for evaluation.

 Our initial architecture sketches for both lm-buddy and Lumigator included an inference server and evaluation library that hits the server for evaluation, which has since evolved into the evaluation job and deployment serving endpoints in Lumigator.

As an evaluation platform, we will always need a way for users to test out models by typing some prompts in a test box for their use-cases, just to see if initial results are good before they move onto systematic evaluation. In evaluating large language models, people need an interactive way to work with the data, a hypothesis that’s been proven out by the success of chatbot apps like ChatGPT/Claude/Gemini, interactive local tools like Ollama, and LmSys Chatbot arena, which allows for visual inspection of prompts.

## How Does Ray Serve Work?

Ray Serve allows you the ability to serve a model with code that gets sent using bundled Ray actors known as deployments. A Deployment is served usually on top of Kubernetes, on top of Ray, within a cluster.

It’s made up of several Ray Actors, which are stateful services run and managed by the Ray control plane. The Controller acts as the entrypoint for the deployment, tied to a proxy on the head node of a Ray cluster, and forwards it to replicas which serve a request with an instantiated model. In order to serve a deployment, you can use the pattern of specifying a YAML-base config, which then gets passed when the deployment is instantiated.

## Specifics

The `summarizer.py` serves the inference code to load the `BART` model using args passed to the model.
The summarizer is bundled as an executable and shipped to the Ray cluster to serve replicas. The organizing code is under `deployments` in the API.
The configuration for the summarizer is at `lumigator/python/mzai/backend/api/deployments/summarizer_config_loader.py`
