import logging
import os

from fastapi import FastAPI
from ray import serve
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.entrypoints.logger import RequestLogger
from vllm.entrypoints.openai.cli_args import make_arg_parser
from vllm.entrypoints.openai.protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
)
from vllm.entrypoints.openai.serving_chat import OpenAIServingChat
from vllm.entrypoints.openai.serving_models import BaseModelPath, LoRAModulePath, OpenAIServingModels, PromptAdapterPath
from vllm.utils import FlexibleArgumentParser

logger = logging.getLogger("ray.serve")

app = FastAPI()


@serve.deployment(name="VLLMDeployment")
@serve.ingress(app)
class VLLMDeployment:
    def __init__(
        self,
        engine_args: AsyncEngineArgs,
        response_role: str,
        lora_modules: list[LoRAModulePath] | None = None,
        prompt_adapters: list[PromptAdapterPath] | None = None,
        request_logger: RequestLogger | None = None,
        chat_template: str | None = None,
    ):
        # See: https://github.com/vllm-project/vllm/issues/8402#issuecomment-2489432973
        if "CUDA_VISIBLE_DEVICES" in os.environ:
            del os.environ["CUDA_VISIBLE_DEVICES"]

        logger.info(f"Starting with engine args: {engine_args}")
        self.openai_serving_chat = None
        self.engine_args = engine_args
        self.response_role = response_role
        self.lora_modules = lora_modules
        self.prompt_adapters = prompt_adapters
        self.request_logger = request_logger
        self.chat_template = chat_template

        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    @app.post("/v1/chat/completions")
    async def create_chat_completion(self, request: ChatCompletionRequest, raw_request: Request):
        """OpenAI-compatible HTTP endpoint.

        API reference:
            - https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
        """
        if not self.openai_serving_chat:
            model_config = await self.engine.get_model_config()
            logger.info(f"Model config: {model_config}")

            # Determine the name of the served model for the OpenAI client.
            model_path = BaseModelPath(self.engine_args.served_model_name[0], self.engine_args.model)
            logger.info(f"Serving model: {model_path}")

            models = OpenAIServingModels(
                engine_client=self.engine,
                model_config=model_config,
                base_model_paths=[model_path],
                lora_modules=self.lora_modules,
                prompt_adapters=self.prompt_adapters,
            )

            self.openai_serving_chat = OpenAIServingChat(
                self.engine,
                model_config,
                models,
                self.response_role,
                request_logger=self.request_logger,
                chat_template=self.chat_template,
                chat_template_content_format="auto",
            )

        logger.info(f"Request: {request}")
        generator = await self.openai_serving_chat.create_chat_completion(request, raw_request)

        if isinstance(generator, ErrorResponse):
            return JSONResponse(content=generator.model_dump(), status_code=generator.code)
        if request.stream:
            return StreamingResponse(content=generator, media_type="text/event-stream")
        else:
            assert isinstance(generator, ChatCompletionResponse)
            return JSONResponse(content=generator.model_dump())


def parse_vllm_args(cli_args: dict[str, str], trust_remote_code: bool):
    """Parses vLLM args based on CLI inputs.

    Currently uses argparse because vLLM doesn't expose Python models for all of the
    config options we want to support.
    """
    arg_parser = FlexibleArgumentParser(description="vLLM OpenAI-Compatible RESTful API server.")

    parser = make_arg_parser(arg_parser)
    arg_strings = []
    for key, value in cli_args.items():
        arg_strings.extend([f"--{key}", str(value)])
    if trust_remote_code:
        arg_strings.extend(["--trust-remote-code"])

    logger.info(arg_strings)
    parsed_args = parser.parse_args(args=arg_strings)
    return parsed_args


def build_app(cli_args: dict[str, str], trust_remote_code: bool = False) -> serve.Application:
    """Builds the Serve app based on CLI arguments.

    See https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#command-line-arguments-for-the-server
    for the complete set of arguments.

    Supported engine arguments: https://docs.vllm.ai/en/latest/models/engine_args.html.
    """  # noqa: E501
    parsed_args = parse_vllm_args(cli_args, trust_remote_code)
    engine_args = AsyncEngineArgs.from_cli_args(parsed_args)
    engine_args.worker_use_ray = True

    return VLLMDeployment.bind(
        engine_args,
        parsed_args.response_role,
        parsed_args.lora_modules,
        parsed_args.prompt_adapters,
        cli_args.get("request_logger"),
        parsed_args.chat_template,
    )


model = build_app(
    {
        "model": os.environ["MODEL_ID"],
        "served-model-name": os.environ["SERVED_MODEL_NAME"],
        "tensor-parallel-size": os.environ["TENSOR_PARALLELISM"],
        "pipeline-parallel-size": os.environ["PIPELINE_PARALLELISM"],
        "dtype": os.environ["DTYPE"],
        "gpu-memory-utilization": os.environ["GPU_MEMORY_UTILIZATION"],
        "distributed_executor_backend": os.environ["DISTRIBUTED_EXECUTOR_BACKEND"],
    },
    trust_remote_code=True if os.getenv("TRUST_REMOTE_CODE", None) == "true" else False,
)
