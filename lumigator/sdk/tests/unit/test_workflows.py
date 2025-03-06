import unittest
from http import HTTPMethod
from unittest.mock import MagicMock, patch

from lumigator_sdk.workflows import Workflows


class TestWorkflows(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.workflows = Workflows(self.mock_client)

    def test_delete_workflow_default_params(self):
        """Test deleting a workflow with default parameters."""
        workflow_id = "test-workflow-123"

        self.workflows.delete_workflow(workflow_id)

        # Verify client was called correctly
        self.mock_client.get_response.assert_called_once_with(
            f"workflows/{workflow_id}", HTTPMethod.DELETE, params={"force": False}
        )

    def test_delete_workflow_with_force_true(self):
        """Test deleting a workflow with force=True."""
        workflow_id = "test-workflow-456"

        self.workflows.delete_workflow(workflow_id, force=True)

        # Verify client was called with force=True
        self.mock_client.get_response.assert_called_once_with(
            f"workflows/{workflow_id}", HTTPMethod.DELETE, params={"force": True}
        )

    def test_delete_workflow_with_force_false(self):
        """Test explicitly setting force=False."""
        workflow_id = "test-workflow-789"

        self.workflows.delete_workflow(workflow_id, force=False)

        # Verify client was called with force=False
        self.mock_client.get_response.assert_called_once_with(
            f"workflows/{workflow_id}", HTTPMethod.DELETE, params={"force": False}
        )

    @patch("lumigator_sdk.workflows.ApiClient")
    def test_delete_workflow_params_passed_to_api(self, mock_api_client):
        """Test that parameters are correctly passed through to the API client."""
        # Setup mock API client
        mock_client = MagicMock()
        mock_api_client.return_value = mock_client

        workflows = Workflows(mock_client)
        workflow_id = "test-workflow-999"

        # Call with force=True
        workflows.delete_workflow(workflow_id, force=True)

        # Verify params dictionary was passed correctly
        mock_client.get_response.assert_called_once()
        call_args = mock_client.get_response.call_args
        self.assertEqual(call_args[0][0], f"workflows/{workflow_id}")
        self.assertEqual(call_args[0][1], HTTPMethod.DELETE)
        self.assertEqual(call_args[1]["params"], {"force": True})
