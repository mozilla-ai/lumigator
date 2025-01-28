import json
from http import HTTPStatus
from pathlib import Path

from lumigator_sdk.health import Health
from pytest import raises
from requests import Response
from requests.exceptions import HTTPError


def test_sdk_healthcheck_ok(lumi_client, request_mock):
    deployment = "local"
    status = "ok"
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Health.HEALTH_ROUTE}",
        status_code=HTTPStatus.OK,
        json={"deployment_type": deployment, "status": status},
    )
    check = lumi_client.health.healthcheck()
    assert check.status == status
    assert check.deployment_type == deployment


def test_sdk_healthcheck_server_error(lumi_client, request_mock):
    response = Response()
    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error = HTTPError(response=response)
    request_mock.get(url=lumi_client.client._api_url + f"/{Health.HEALTH_ROUTE}", exc=error)
    with raises(HTTPError):
        result = lumi_client.health.healthcheck()
        print(result)


def test_sdk_healthcheck_missing_deployment(lumi_client, request_mock):
    status = "ok"
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Health.HEALTH_ROUTE}",
        status_code=HTTPStatus.OK,
        json={"status": status},
    )
    check = lumi_client.health.healthcheck()
    assert check.status == status
    assert check.deployment_type is None
