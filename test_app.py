from unittest.mock import Mock

from app import create_branch_handler


def test_create_pr():
    event = Mock()
    event.repository.default_branch = "master"
    event.ref = "feature"
    create_branch_handler(event)
    event.repository.create_pull.assert_called_once_with(
        "master",
        "feature",
        title="feature",
        body="PR automatically created",
        draft=False,
    )
