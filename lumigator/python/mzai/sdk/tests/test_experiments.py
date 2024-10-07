import importlib.resources
import json
import unittest.mock as mock
from http import HTTPStatus
from pathlib import Path

from pytest import raises
from requests.exceptions import HTTPError

from tests.helpers import load_request, load_response

def test_get_experiments_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiments.json")
    experiments_ret = lumi_client.experiments.get_experiments()
    assert experiments_ret is not None


def test_get_experiment_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiment.json")
    experiment_ret = lumi_client.experiments.get_experiment()
    assert experiment_ret is not None


def test_create_experiment_ok_simple(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiment-post-response.json")
    experiment_ret = lumi_client.experiments.create_experiment(load_request("data/experiment-post-simple.json"))
    assert experiment_ret is not None


def test_create_experiment_ok_all(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiment-post-response.json")
    experiment_ret = lumi_client.experiments.create_experiment(load_request("data/experiment-post-all.json"))
    assert experiment_ret is not None

