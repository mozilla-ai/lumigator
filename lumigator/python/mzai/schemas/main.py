"""this is a work in progress of an sdk and CLI for lumigator.

Build it:

```
pants package lumigator:lumigator_bin
```

Run it via pants (useful if you're debugging)
```
pants run lumigator:lumigator_bin
```

when you build or run the above target, pants puts it in `./dist/lumigator`. you can run it like

```
lumigator/lumigator_bin.pex --help
```

@vicki, @mario - if you launch docker compose, you can use this file to run
commands like

```
LUMIGATOR_SERVICE_HOST=127.0.0.1 \
RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR=localhost \
  dist/lumigator/lumigator_bin.pex groundtruth --list
```

perhaps from another container or just from make. you can add a make target like
I did.


> make local-up

> LUMIGATOR_SERVICE_HOST=127.0.0.1 \
    RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR=localhost  \
    pants run lumigator:lumigator_bin -- groundtruth --list

the target
`lumigator:lumigator_bin` is a pex binary which can be executed as if it were a
single-file binary. there's also a wheel target that can be distributed.

"""

import dataclasses
import json
import logging
import os
from functools import wraps
from pathlib import Path
from typing import Any, Dict, TypeVar  # noqa: UP035
from urllib.parse import urlparse, urlunparse
from uuid import UUID

import click
import pandas as pd
import requests
from pydantic import BaseModel

from .datasets import DatasetResponse
from .experiments import ExperimentResponse, ExperimentResultDownloadResponse
from .extras import ListingResponse
from .groundtruth import GroundTruthDeploymentResponse

ParentBaseModel = TypeVar("ParentBaseModel", DatasetResponse, ExperimentResponse, BaseModel)
LOGGER = logging.getLogger(__name__)
# def get_ray_link(job_id: UUID, RAY_SERVER_URL: str) -> str:
#     return f"{RAY_SERVER_URL}/#/jobs/{job_id}"
#
#
# def has_field(model: BaseModel, field: str) -> bool:
#     """Check if a Pydantic model class has a field with the given name."""
#     return field in model.__fields__
#
#
# def get_resource_id(response: requests.Response) -> UUID:
#     if response.status_code == requests.codes.created:
#         return json.loads(response.text).get("id")
#


# @dataclasses.dataclass
# class LumigatorParser:
#     pydantic_schema: BaseModel
#     api_route: APIRouter
#     method: str
#
#
# class PathParam:
#     def __init__(self, s):
#         if s.startswith("{") and s.endswith("}"):
#             self.is_param = True
#             self.value = s[1:-1]
#         else:
#             raise ValueError("not a param")
#
#
# # - BASE --------------------------------------------------------------
# def resolver(url: str):
#     """An attempt was made.
#
#     ' object is not iterable
#     [m for m in router.__dir__()]
#     [
#      'APIRouter', 'datasets', 'events', 'experiments', 'finetuning', 'groundtruth', 'health',
#      ]
#      router.groundtruth.router.__dict__
#     {'routes': [
#     APIRoute(path='/deployments', name='create_groundtruth_deployment', methods=['POST']),
#     APIRoute(path='/deployments', name='list_groundtruth_deployments', methods=['GET']),
#     APIRoute(path='/deployments/{deployment_id}', name='send_model_request', methods=['POST']),
#     APIRoute(path='/deployments/{deployment_id}', name='delete_deployment', methods=['DELETE'])]
#     """
#
#     def parse_module_from_path(path):
#         prefix = ("/", "api", "v1")
#         match Path(path).parts:
#             case ("/", "api", "v1", module):
#                 module = module
#             case ("/", "api", "v1", module, *rest):
#                 module = module
#             case _:
#                 module = None
#         return module
#
#     def get_class_from_path_and_name(p: str, name: str) -> Callable:
#         module_name = parse_module_from_path(p)
#         m = getattr(router_module, module_name)
#         return getattr(m, name)
#
#     def parse_parent_router(r: APIRouter, path: str) -> LumigatorParser:
#         if isinstance(r, APIRouter):
#             for route in r.routes:
#                 match route:
#                     case APIRoute(path=p, name=n, methods=ms):
#                         module = parse_module_from_path(p)
#                         model_class = get_class_from_path_and_name(p, n)
#                         lp = LumigatorParser(model_class, route, ms[0])
#                     case _:
#                         lp = None
#         return lp
#
#     parser = parse_parent_router(url)
#     return parser


def match_url(url):
    new_url = None
    local = ("localhost", "192.168.0.1")
    parsed = urlparse(url)
    match URLComponents(*parsed):
        case URLComponents(scheme=scheme, netloc="", path=path, params="", query="", fragment=""):
            # This is a little annoying.
            # we are assigning s as the matched schema and p as path.
            # s can still be empty "".
            # then we match again on a new tuple.
            # >>> from urllib.parse import urlparse
            # >>> urlparse("localhost")
            # >>> ParseResult(scheme='', netloc='', path='localhost', params='',
            #                 query='', fragment='')
            # >>> urlparse("localhost:80")
            # >>> ParseResult(scheme='localhost', netloc='', path='80', params='',
            #                 query='', fragment='')

            match (scheme, path.split(":")):
                # like url = "localhost:80"
                case ("", [netloc, port]):
                    new_url = URLComponents(netloc=netloc, port=port).to_url()
                    logging.debug(f"Matched URL: {new_url} - '', [netloc, port]")
                # like url = "localhost" - parser says that's the path
                case ("", [netloc]):
                    if netloc in local:
                        new_url = URLComponents(netloc=netloc).to_url()
                        logging.debug(f"Matched URL: {new_url} - ('', [netloc])")
                    else:
                        new_url = URLComponents(netloc=netloc).to_url()
                        logging.debug(f"Matched URL: {new_url} - ('', [netloc])")

                case (netloc, [maybe_port]) if maybe_port.isalnum():
                    new_url = URLComponents(netloc=netloc, port=maybe_port).to_url()
                    logging.debug(f"Matched URL: {new_url} - (netloc, [maybe_port])")

                case (netloc, [actually_path]):
                    new_url = URLComponents(netloc=netloc, path=actually_path).to_url()
                    logging.debug(f"Matched URL: {new_url} - (netloc, [actually_path])")
                case _:
                    raise ValueError(
                        f"error parsing {scheme} and {path} from {parsed} - catchall case"
                    )

        case URLComponents(scheme=scheme, netloc=netloc, path=path, params=params):
            new_url = URLComponents(scheme=scheme, netloc=netloc, path=path, params=params).to_url()
            logging.warning(f"Matched URL: {new_url} - discarding ")

        case URLComponents(scheme=scheme, netloc=netloc, path=path, params=""):
            new_url = URLComponents(scheme=scheme, netloc=netloc, path=path).to_url()
            logging.warning(f"Matched URL: {new_url} - no params")

        case URLComponents(scheme=scheme, netloc=netloc):
            new_url = URLComponents(scheme=scheme, netloc=netloc).to_url()
            logging.warning(f"Matched URL: {new_url} - no path or more")

        case URLComponents(scheme="http", netloc=netloc):
            new_url = URLComponents(netloc=netloc).to_url()
            logging.warning(f"Matched URL: {new_url} - only netloc")

        case _:
            raise ValueError(f"can't parse: {parsed}")
    return new_url


@dataclasses.dataclass
class URLComponents:
    """This is a bit overkill.

    For sure. This is mostly here to help take *flexible*
    args from the env, like if you set just `LOCALHOST` or whatever.
    This is probably not really needed eventually, as i want to
    dynamically generate all the stuff anyway.
    """

    scheme: str = "http"
    netloc: str = ""
    path: str = ""
    params: dict = ""
    query: str = ""
    fragment: str = ""
    port: int | str | None = None

    __match_args__: tuple[str, ...] = (
        "scheme",
        "netloc",
        "path",
        "params",
        "query",
        "fragment",
        "port",
    )

    def __post_init__(self):
        """Overrides the port."""
        if self.port != "" and self.port is not None:
            if len(self.netloc.split(":")) == 1:
                self.netloc = self.netloc + ":" + self.port

    def to_url(self):
        """This should be obvious."""
        url = urlunparse(
            (self.scheme, self.netloc, self.path, self.params, self.query, self.fragment)
        )

        return url


class _LumigatorClient:
    def __init__(
        self,
        api_host: str | None = None,
        ray_host: str | None = None,
        s3_base_path: str | None = None,
    ):
        """Base class to hold methods to send requests to the Lumigator API.

        Args:
        api_host: hostname of the Lumigator backend api. reads from Env
        ray_host: head node of your ray cluster. reads from Env
        s3_base_path: base path for where s3 files are stored
        """
        self.api_host = api_host or os.getenv("LUMIGATOR_SERVICE_HOST")  # error if none
        self.ray_head_host = ray_host or os.getenv("RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR")

        if self.api_host is None or self.ray_head_host is None:
            raise ValueError(
                f"api or ray host error: api_host={self.api_host}, ray_host={self.ray_head_host}"
            )

        self.ray_service_url = match_url(self.ray_head_host)
        # self.api_url = match_url(self.api_host)
        self.api_url = URLComponents(scheme="http", netloc=self.api_host, path="api/v1").to_url()

        # base S3 path
        self.s3_base_path = (
            s3_base_path or os.getenv("S3_BASE_PATH")
        ) or "lumigator-storage/experiments/results/"

    def make_request(
        self,
        route: str | Path,
        method: str = "GET",
        params: Dict[str, Any] = None,  # noqa: UP006
        data: Dict[str, Any] = None,  # noqa: UP006
        files: Dict[str, Any] = None,  # noqa: UP006
        headers: Dict[str, str] = None,  # noqa: UP006
        json_: Dict[str, str] = None,  # noqa: UP006
        timeout: int = 10,
        raw_url: str | Path = None,
        pydantic_model: ParentBaseModel | None = None,
        *args,
        **kwargs,
    ) -> ParentBaseModel:
        """Make an HTTP request using the requests library.

        Args:
            route: the internal route that goes *after* the base api.
            method: The HTTP method to use. Defaults to "GET".
            params: URL parameters to include in the request.
            data: Data to send in the request body.
            files: Files to send in the request body.
            headers: Headers to include in the request.
            json_: JSON data to include in the request.
            timeout: Timeout for the request in seconds. Defaults to 10.
            raw_url: if this is passed, make a request with this instead
            of the route arg.

        Returns:
            requests.Response: The response object from the request.

        Raises:
            requests.RequestException
        """
        url = f"{self.api_url}/{route}" if raw_url is None else raw_url
        logging.debug(
            f"Request: {url}, params: {params}, data: {data}, files: {files}, headers: {headers}"
        )

        try:
            response = requests.request(
                *args,
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                files=files,
                headers=headers,
                timeout=timeout,
                json=json_,
                **kwargs,  # noqa: B026
            )
            response.raise_for_status()
            logging.debug(f"{json.dumps(response.json(), indent=2)}")
        except requests.RequestException as e:
            raise requests.RequestException("Cannot complete your request as executed.") from e
        # a tiny cache, as a treat
        self._last_api_response = response
        if pydantic_model is not None:
            # requires strings, not dicts
            return pydantic_model.model_validate_json(response.text)
        else:
            return response.json()


class Datasets(_LumigatorClient):
    def __init__(self, *args, **kwargs):
        """Used to wrap the Datasets endpoint."""
        super().__init__(*args, **kwargs)

    def upload(self, filename) -> DatasetResponse:
        with Path(filename).open("rb") as f:
            files = {"dataset": f}
            payload = {"format": "experiment"}
            route = "datasets"
            return self.make_request(
                route=route,
                method="POST",
                data=payload,
                files=files,
                pydantic_model=DatasetResponse,
            )

    def info(self, dataset_id: UUID) -> DatasetResponse:
        return self.make_request(route="datasets/{dataset_id}", pydantic_model=DatasetResponse)


class Experiments(_LumigatorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def submit(
        self,
        model_name: str,
        name: str,
        description: str | None,
        dataset_id: UUID,
        max_samples: int = 10,
    ) -> ExperimentResponse:
        payload = {
            "name": name,
            "description": description,
            "model": model_name,
            "dataset": dataset_id,
            "max_samples": max_samples,
        }

        return self.make_request(
            "experiments",
            method="POST",
            data=json.dumps(payload),
            pydantic_model=ExperimentResponse,
        )

    def info(self, experiment_id: UUID) -> ExperimentResponse:
        return self.make_request(f"experiments/{experiment_id}", pydantic_model=ExperimentResponse)

    def result_download(self, experiment_id: UUID) -> ExperimentResultDownloadResponse:
        er = self.make_request(
            f"/experiments/{experiment_id}/result/download",
            verbose=False,
            pydantic_model=ExperimentResultDownloadResponse,
        )
        # boto3 returns download URLs with default port, CW does not have it
        # (this is ugly but does not affect local or AWS setups)
        download_url = er.download_url.replace(
            "object.lga1.coreweave.com:4566", "object.lga1.coreweave.com"
        )

        download_response = self.make_request(
            raw_url=download_url, verbose=False, pydantic_model=None
        )
        exp_results = json.loads(download_response.text)
        self._exp_results = exp_results
        return exp_results

    @classmethod
    def convert_eval_results_to_table(cls, models, eval_results):
        """Format evaluation results jsons into one pandas dataframe."""
        # metrics dict format is
        # "column name": [list of keys to get val in nested results dict]
        metrics = {
            "Meteor": ["meteor", "meteor_mean"],
            "BERT Precision": ["bertscore", "precision_mean"],
            "BERT Recall": ["bertscore", "recall_mean"],
            "BERT F1": ["bertscore", "f1_mean"],
            "ROUGE-1": ["rouge", "rouge1_mean"],
            "ROUGE-2": ["rouge", "rouge2_mean"],
            "ROUGE-L": ["rouge", "rougeL_mean"],
        }

        def parse_model_results(model, results):
            row = {}
            row["Model"] = model.replace("hf://", "")

            for column, metric in metrics.items():
                temp_results = results
                for key in metric:
                    value = temp_results.get(key)
                    if value is None:
                        break
                    temp_results = value

                row[column] = value
            return row

        eval_table = []
        for model, results in zip(models, eval_results, strict=True):
            eval_table.append(parse_model_results(model, results))

        return pd.DataFrame(eval_table)


class GroundTruth(_LumigatorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list(self):
        return self.make_request(
            route="ground-truth/deployments",
            method="GET",
            # this is the pattern for list resonses - need to wrap them like this.
            pydantic_model=ListingResponse[GroundTruthDeploymentResponse],
        )


class LumigatorClient:
    def __init__(self, *args, **kwargs):
        """This is a bit weird and probably needs to get redesigned at some point.

        It's remaking the client stuff in each faux child and all that - can just make a
        client for making requests and move the shared arg stuff here. This is what happens when
        you hack hack hack.

        You can use it like:
        >>> lc = LumigatorClient()
        >>> lc.experiments.submit(*args, **kwargs)
        """
        self.experiments = Experiments(*args, **kwargs)
        self.datasets = Datasets(*args, **kwargs)
        self.groundtruth = GroundTruth(*args, **kwargs)


def common_options(f):
    """Weird things for Click."""

    @wraps(f)
    @click.option("--api-host", default=None)
    @click.option("--ray-host", default=None)
    @click.option("--s3-base-path", default=None)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--debug/--no-debug", default=False)
def cli(ctx, debug):  # noqa: D103
    """CLI for interacting with a Lumigator backend."""
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        click.secho("root lumigator cli function called- exiting", fg="bright_green")
    logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)


@cli.command(name="datasets")
@common_options
@click.option("--upload", help="Submit dataset")
@click.option("--info", help="download results")
def datasets_command(
    upload, info, api_host=None, ray_host=None, s3_base_path=None, *args, **kwargs
) -> ParentBaseModel:
    """These will eventually need a redesign to be a little less crazy.

    If we generate the sdk code we can make these args to follow the semantics
    of Lumigator's api.
    """
    opts = {"api_host": api_host, "ray_host": ray_host, "s3_base_path": s3_base_path}
    c = LumigatorClient(**opts).datasets
    if upload:
        res = c.upload(upload)
    elif info:
        res = c.info(info)

    else:
        res = None
    return res


@cli.command(name="experiments")
@common_options
@click.option("--submit", help="Submit dataset")
@click.option("--info", help="download results")
@click.option("--download", help="download results")
def experiments_command(submit, info, download, *args, **kwargs) -> DatasetResponse | None:
    opts = {
        "api_host": kwargs.get("api_host"),
        "ray_host": kwargs.get("ray_host"),
        "s3_base_path": kwargs.get("s3_base_path"),
    }
    c = LumigatorClient(**opts).experiments
    res = None
    if submit:
        res = c.submit(submit)
    elif info:
        res = c.info(info)
    elif download:
        res = c.result_download(info)
    else:
        pass
    return res


@cli.command(name="groundtruth")
@common_options
@click.option("--list", help="list your deployments", is_flag=True)
def groundtruth_command(list, *args, **kwargs) -> DatasetResponse | None:
    opts = {
        "api_host": kwargs.get("api_host"),
        "ray_host": kwargs.get("ray_host"),
        "s3_base_path": kwargs.get("s3_base_path"),
    }
    c = LumigatorClient(**opts).groundtruth
    res = None
    if list:
        res = c.list()
    else:
        pass
    print(res)
    return res


if __name__ == "__main__":
    cli(auto_envvar_prefix="LUMIGATOR_SDK_")
