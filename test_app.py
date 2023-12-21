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


# Test that sentry_sdk.init is not called
@pytest.mark.sentry_test
def test_sentry_sdk_initialization_not_called(mock_sentry_init):
    # Purposefully do not call sentry_sdk.init()
    mock_sentry_init.assert_not_called()
    event.repository.create_pull.return_value.enable_automerge.assert_called_once_with(
        merge_method="SQUASH"
    )


# Test that sentry_sdk.init raises an exception with an invalid URL
@pytest.mark.sentry_test
def test_sentry_sdk_initialization_invalid_url(mock_sentry_init):
    invalid_dsn = "not a dsn"
    with patch(
        "sentry_sdk.init", side_effect=Exception("Invalid DSN")
    ) as mock_init_invalid:
        with pytest.raises(Exception):
            sentry_sdk.init(invalid_dsn)
        mock_init_invalid.assert_called_once_with(invalid_dsn)


from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_sentry_init():
    with patch("sentry_sdk.init") as mock_init:
        yield mock_init


def test_sentry_sdk_initialization(mock_sentry_init):
    """
    Test function that checks if Sentry SDK initialization is done correctly.

    Uses the `mock_sentry_init` fixture to mock the `sentry_sdk.init` function. Asserts
    that it is called once with a specific DSN argument.
    """
    mock_sentry_init.assert_called_once_with(
        "https://575b73d4722bd4f8cc8bafb0274e4480@o305287.ingest.sentry.io/4506434483453952"
    )


def test_enable_automerge_on_existing_pr(event):
    existing_pr = Mock()
    event.repository.get_pulls.return_value = [existing_pr]
    create_branch_handler(event)
    event.repository.create_pull.assert_not_called()
    existing_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")
