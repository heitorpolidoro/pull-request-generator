from unittest.mock import patch

import pytest

from app import create_branch_handler


@pytest.fixture
def repo():
    with patch("github.Repository.Repository") as Repository:
        repository = Repository()
        repository.default_branch = "master"
        yield repository


def test_create_pr(repo):
    create_branch_handler()
    repo.create_pull.assert_called_once_with(
        "master",
        "feature",
        title="feature",
        body="PR automatically created",
        draft=False,
    )
