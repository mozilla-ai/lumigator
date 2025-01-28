import json
from http import HTTPStatus

from lumigator_sdk.completions import Completions
from pytest import raises
from tests.helpers import load_json


def test_get_vendors_ok(lumi_client, mock_vendor_data, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )

    vendors = lumi_client.completions.get_vendors()

    assert vendors is not None
    assert len(vendors) == 2
    assert "openai" in vendors
    assert "mistral" in vendors


def test_get_vendors_none(lumi_client, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=[],
    )

    vendors = lumi_client.completions.get_vendors()
    assert vendors is not None
    assert vendors == []


def test_get_completion_invalid_vendor(lumi_client, mock_vendor_data, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )

    with raises(ValueError):
        lumi_client.completions.get_completion("foo", "test")


def test_get_completion_invalid_vendor_empty(lumi_client, mock_vendor_data, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )

    with raises(ValueError):
        lumi_client.completions.get_completion("", "test")


def test_get_completion_invalid_text_empty(lumi_client, mock_vendor_data, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )

    with raises(ValueError):
        lumi_client.completions.get_completion("openai", "")


def test_get_completion_invalid_text_spacey(lumi_client, mock_vendor_data, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )

    with raises(ValueError):
        lumi_client.completions.get_completion("openai", "  ")


def test_get_completion_openai_ok(lumi_client, mock_vendor_data, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )

    lumi_client.completions.get_vendors()
    vendor = "openai"

    request_mock.post(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}/{vendor}/",
        status_code=HTTPStatus.OK,
        json={"text": "thanks"},
    )

    response = lumi_client.completions.get_completion(vendor, "please")
    assert response is not None
    assert response.text == "thanks"


def test_get_completion_mistral_ok(lumi_client, mock_vendor_data, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )

    lumi_client.completions.get_vendors()
    vendor = "mistral"

    request_mock.post(
        url=lumi_client.client._api_url + f"/{Completions.COMPLETIONS_ROUTE}/{vendor}/",
        status_code=HTTPStatus.OK,
        json={"text": "thanks"},
    )

    response = lumi_client.completions.get_completion("mistral", "please")
    assert response is not None
    assert response.text == "thanks"
