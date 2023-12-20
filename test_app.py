from unittest.mock import Mock

from app import create_branch_handler


def test_create_pr():
    event = Mock()
    event.repository.default_branch = "master"
    event.ref = "feature"
    create_branch_handler(event)
    event.repository.get_pulls = Mock(return_value=[Mock()])
    create_branch_handler(event)
    if event.repository.get_pulls.return_value:
        event.repository.get_pulls.return_value[0].enable_automerge.assert_called_once()
    else:
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
