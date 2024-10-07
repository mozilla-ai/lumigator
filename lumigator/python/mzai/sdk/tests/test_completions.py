import json

from pytest import raises


def test_get_vendors_ok(mock_requests_response, mock_requests, lumi_client, mock_vendor_data):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(mock_vendor_data)

    vendors = lumi_client.completions.get_vendors()

    assert vendors is not None
    assert len(vendors) == 2
    assert "openai" in vendors
    assert "mistral" in vendors


def test_get_vendors_none(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    vendors = lumi_client.completions.get_vendors()
    assert vendors is not None
    assert vendors == []


def test_get_completion_invalid_vendor(
    mock_requests_response, mock_requests, lumi_client, mock_vendor_data
):
    # Mock vendors response.
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(mock_vendor_data)

    with raises(ValueError):
        lumi_client.completions.get_completion("foo", "juan?")


def test_get_completion_invalid_text_empty(
    mock_requests_response, mock_requests, lumi_client, mock_vendor_data
):
    # Mock vendors response.
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(mock_vendor_data)

    with raises(ValueError):
        lumi_client.completions.get_completion("openai", "")


def test_get_completion_invalid_text_spacey(
    mock_requests_response, mock_requests, lumi_client, mock_vendor_data
):
    # Mock vendors response.
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(mock_vendor_data)

    with raises(ValueError):
        lumi_client.completions.get_completion("openai", "  ")
