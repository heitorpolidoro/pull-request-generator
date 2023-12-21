from unittest.mock import Mock

import pytest
import sentry_sdk

from app import create_branch_handler


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


from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_sentry_init():
    with patch('sentry_sdk.init') as mock_init:
        yield mock_init

def test_sentry_sdk_initialization(mock_sentry_init):
    mock_sentry_init.assert_called_once_with('https://575b73d4722bd4f8cc8bafb0274e4480@o305287.ingest.sentry.io/4506434483453952')

def test_enable_automerge_on_existing_pr(event):
    existing_pr = Mock()
    event.repository.get_pulls.return_value = [existing_pr]
    create_branch_handler(event)
    event.repository.create_pull.assert_not_called()
    existing_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")
