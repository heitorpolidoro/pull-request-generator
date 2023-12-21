from unittest.mock import Mock

import pytest

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


def test_enable_automerge_on_existing_pr(event):
    existing_pr = Mock()
    event.repository.get_pulls.return_value = [existing_pr]
    create_branch_handler(event)
    event.repository.create_pull.assert_not_called()
    existing_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")
