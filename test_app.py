from unittest import TestCase
from unittest.mock import Mock, patch

import pytest
import sentry_sdk
from github import GithubException

from app import app, create_branch_handler


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
    event.repository.create_pull.return_value.enable_automerge.assert_called_once_with(
        merge_method="SQUASH"
    )


def test_create_pr_no_commits(event):
    event.repository.get_pulls.return_value = []
    event.repository.create_pull.side_effect = GithubException(
        422,
        message="No commits between 'master' and 'feature'"
    )
    create_branch_handler(event)


def test_create_pr_other_exceptions(event):
    event.repository.get_pulls.return_value = []
    event.repository.create_pull.side_effect = GithubException(
        422,
        message="Other exception"
    )
    with pytest.raises(GithubException):
        create_branch_handler(event)


def test_enable_just_automerge_on_existing_pr(event):
    existing_pr = Mock()
    event.repository.get_pulls.return_value = [existing_pr]
    create_branch_handler(event)
    event.repository.create_pull.assert_not_called()
    existing_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")


class TestApp(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        sentry_sdk.flush()

    def test_root(self):
        """
        Test the root endpoint of the application.
        This test ensures that the root endpoint ("/") of the application is working correctly.
        It sends a GET request to the root endpoint and checks that the response status code is 200 and the response text is "Pull Request Generator App up and running!".
        """
        response = self.app.get("/")
        assert response.status_code == 200
        assert response.text == "Pull Request Generator App up and running!"

    def test_webhook(self):
        """
        Test the webhook handler of the application.
        This test ensures that the webhook handler is working correctly.
        It mocks the `handle` function of the `webhook_handler` module, sends a POST request to the root endpoint ("/") with a specific JSON payload and headers, and checks that the `handle` function is called with the correct arguments.
        """
        with patch("app.webhook_handler.handle") as mock_handle:
            request_json = {"action": "opened", "number": 1}
            headers = {
                "User-Agent": "Werkzeug/3.0.1",
                "Host": "localhost",
                "Content-Type": "application/json",
                "Content-Length": "33",
                "X-Github-Event": "pull_request",
            }
            self.app.post("/", headers=headers, json=request_json)
            mock_handle.assert_called_once_with(headers, request_json)
