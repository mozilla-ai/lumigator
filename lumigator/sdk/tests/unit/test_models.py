from http import HTTPStatus

from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse
from lumigator_sdk.lumigator import LumigatorClient
from lumigator_sdk.models import Models
from pytest import raises
from requests import Response
from requests.exceptions import HTTPError
from tests.helpers import load_json


def test_sdk_suggested_models_ok(
    lumi_client: LumigatorClient, json_data_models: ListingResponse[ModelsResponse], request_mock
):
    task = "summarization"
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Models.MODELS_ROUTE}/{task}",
        status_code=HTTPStatus.OK,
        json=json_data_models,
    )

    models = lumi_client.models.get_suggested_models(task)
    assert models is not None


def test_sdk_suggested_models_invalid_task(lumi_client, request_mock):
    task = "invalid_task"
    response = Response()
    response.status_code = HTTPStatus.BAD_REQUEST
    error = HTTPError(response=response)
    request_mock.get(url=lumi_client.client._api_url + f"/{Models.MODELS_ROUTE}/{task}", exc=error)

    with raises(HTTPError):
        lumi_client.models.get_suggested_models(task)
