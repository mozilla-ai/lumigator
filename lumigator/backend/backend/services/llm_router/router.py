import abc
import functools

from huggingface_hub import hf_hub_download
from lumigator_schemas.llm_router import ModelPair, RouterModelConfigRequest

from backend.services.llm_router.model import CausalLLMClassifier
from backend.services.llm_router.utils import load_prompt_format, to_openai_api_messages
from backend.services.secrets import SecretService


class RouterServiceFactory:
    def __init__(self, secret_service: SecretService):
        self.secret_service = secret_service

    def create_router(self, config: RouterModelConfigRequest):
        router_type = config.router_definition.router_type
        router_cls = ROUTER_CLS[router_type]
        return router_cls(config, self.secret_service)


class RouterService(abc.ABC):
    """Calculate the winrate of the 'pro' model.

    Return a float between 0 and 1 representing the value used to route to models,
    conventionally the winrate of the strong model.

    If this value is >= the user defined cutoff, the router will route to the 'pro' model,
    otherwise, it will route to the 'lite' model.
    """

    threshold: float = 0.5
    routed_pair: ModelPair

    @abc.abstractmethod
    def calculate_strong_win_rate(self, prompt) -> float:
        """Calculate the winrate of the 'pro' model.

        Return a float between 0 and 1 representing the value used to route to models,
        conventionally the winrate of the strong model.

        Args:
            prompt (str): The prompt to calculate the winrate for.
        """
        pass

    def route(self, prompt):
        """Route the prompt to the correct model.

        If the winrate of the 'pro' model is greater than the threshold, route to the 'pro' model,
        otherwise route to the 'lite' model.

        Args:
            - prompt (str): The prompt to route.
        """
        if self.calculate_strong_win_rate(prompt) >= self.threshold:
            return self.routed_pair.pro
        else:
            return self.routed_pair.lite

    def __str__(self):
        """Return the name of the router class."""
        return NAME_TO_CLS[self.__class__]


class CausalLLMRouterService(RouterService):
    def __init__(
        self,
        config: RouterModelConfigRequest,
        secret_service: SecretService = None,
    ):
        router_model_id = config.router_definition.router_model_id
        prompt_format = load_prompt_format(config.router_definition.model_id)

        self.router_model = CausalLLMClassifier(
            config=config,
            prompt_format=prompt_format,
            prompt_field="messages",
            additional_fields=(),
            use_last_turn=True,
            secret_service=secret_service,
        )

        system_message = hf_hub_download(repo_id=router_model_id, filename="system_ft_v5.txt")
        classifier_message = hf_hub_download(repo_id=router_model_id, filename="classifier_ft_v5.txt")

        with open(system_message) as pr:
            system_message = pr.read()
        with open(classifier_message) as pr:
            classifier_message = pr.read()

        self.to_openai_messages = functools.partial(to_openai_api_messages, system_message, classifier_message)

    def calculate_strong_win_rate(self, prompt):
        input = {}
        input["messages"] = self.to_openai_messages([prompt])
        output = self.router_model(input)
        if output is None:
            # Route to strong model if output is invalid
            return 1
        else:
            return 1 - output["binary_prob"]


class MatrixFactorizationRouterService(RouterService):
    pass


class SWRanikngRouterService(RouterService):
    pass


class BertRouterService(RouterService):
    pass


ROUTER_CLS = {
    "mf": MatrixFactorizationRouterService,
    "causal-llm": CausalLLMRouterService,
    "bert": BertRouterService,
    "sw_ranking": SWRanikngRouterService,
}
NAME_TO_CLS = {v: k for k, v in ROUTER_CLS.items()}
