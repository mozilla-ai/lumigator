from http import HTTPStatus

from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse
from lumigator_sdk.lumigator import LumigatorClient
from lumigator_sdk.models import Models
from pytest import raises
from requests import Response
from requests.exceptions import HTTPError
from tests.helpers import load_json


def test_get_suggested_models_single_task_ok(
    lumi_client: LumigatorClient, json_data_models: ListingResponse[ModelsResponse], request_mock
):
    tasks = ["summarization"]
    request_mock.get(
        url=f"{lumi_client.client._api_url}/{Models.MODELS_ROUTE}/?tasks={tasks[0]}",
        complete_qs=True,
        status_code=HTTPStatus.OK,
        json=json_data_models,
    )

    models = lumi_client.models.get_suggested_models(tasks)
    assert models is not None


def test_get_suggested_models_multiple_tasks_ok(
    lumi_client: LumigatorClient, json_data_models: ListingResponse[ModelsResponse], request_mock
):
    tasks = ["summarization", "translation"]
    task_params = "&".join([f"tasks={task}" for task in tasks])
    request_mock.get(
        url=f"{lumi_client.client._api_url}/{Models.MODELS_ROUTE}/?{task_params}",
        complete_qs=True,
        status_code=HTTPStatus.OK,
        json=json_data_models,
    )

    models = lumi_client.models.get_suggested_models(tasks)
    assert models is not None


def test_get_suggested_models_no_task_specified(
    lumi_client: LumigatorClient, json_data_models: ListingResponse[ModelsResponse], request_mock
):
    request_mock.get(
        url=f"{lumi_client.client._api_url}/{Models.MODELS_ROUTE}",
        complete_qs=True,
        status_code=HTTPStatus.OK,
        json=json_data_models,
    )

    models = lumi_client.models.get_suggested_models()
    assert models is not None


def test_get_suggested_models_invalid_task(lumi_client, request_mock):
    tasks = ["invalid_task"]
    response = Response()
    response.status_code = HTTPStatus.BAD_REQUEST
    error = HTTPError(response=response)
    request_mock.get(url=f"{lumi_client.client._api_url}/{Models.MODELS_ROUTE}/?tasks={tasks[0]}", exc=error)

    with raises(HTTPError):
        lumi_client.models.get_suggested_models(tasks)
