import json


def test_get_vendors_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads('["openai", "mistral"]')

    vendors = lumi_client.completions.get_vendors()

    assert vendors is not None
    assert len(vendors) == 2
    assert vendors[0] == "openai"
    assert vendors[1] == "mistral"


def test_get_vendors_none(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    vendors = lumi_client.completions.get_vendors()
    assert vendors is not None
    assert vendors == []