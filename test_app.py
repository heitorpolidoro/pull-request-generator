from unittest.mock import Mock, patch

import pytest

from app import app, create_branch_handler, webhook_handler


@pytest.fixture
def event():
    event = Mock()
    event.repository.default_branch = "master"
    event.ref = "feature"
    return event


def test_create_pr(event):
    event.repository.get_pulls.return_value = []
    create_branch_handler(event)
    event.repository.create_pull.assert_called_once_with(
        "master",
        "feature",
        title="feature",
        body="PR automatically created",
        draft=False,
    )


def test_root():
    with patch("app.webhook_handler.root") as mock_root:
        expected_response = "Expected Response"
        mock_root.return_value = expected_response
        response = app.root()
        mock_root.assert_called_once_with("Pull Request Generator")
        assert response == expected_response


def test_webhook():
    with patch("app.request") as mock_request, patch(
        "app.webhook_handler.handle"
    ) as mock_handle:
        mock_request.headers = {"content-type": "application/json"}
        mock_request.json = {"action": "opened", "number": 1}
        app.webhook()
        mock_handle.assert_called_once_with(mock_request.headers, mock_request.json)


def test_enable_automerge_on_existing_pr(event):
    existing_pr = Mock()
    event.repository.get_pulls.return_value = [existing_pr]
    create_branch_handler(event)
    event.repository.create_pull.assert_not_called()
    existing_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")
