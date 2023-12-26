from unittest.mock import Mock, patch

import pytest
from github import GithubException

from app import create_branch_handler


@pytest.fixture
def repository():
    """
    This fixture returns a mock repository object with default values for the attributes.
    :return: Mocked Repository
    """
    repository = Mock()
    repository.default_branch = "master"
    repository.full_name = "heitorpolidoro/pull-request-generator"
    repository.get_pulls.return_value = []
    return repository


@pytest.fixture
def issue():
    """
    This fixture returns a mock issue object with default values for the attributes.
    :return: Mocked Issue
    """
    issue = Mock()
    issue.title = "feature"
    issue.body = "feature body"
    issue.number = 42
    return issue


@pytest.fixture
def event(repository, issue):
    """
    This fixture returns a mock event object with default values for the attributes.
    :return: Mocked Event
    """
    event = Mock()
    event.repository = repository
    event.repository.get_issue.return_value = issue
    event.ref = "issue-42"
    return event


def test_create_pr(event):
    """
    This test case tests the create_branch_handler function when there are commits between the new branch and the
    default branch. It checks that the function creates a pull request with the correct parameters.
    """
    expected_body = """### [feature](https://github.com/heitorpolidoro/pull-request-generator/issues/42)

feature body

Closes #42

"""
    create_branch_handler(event)
    event.repository.create_pull.assert_called_once_with(
        "master",
        "issue-42",
        title="feature",
        body=expected_body,
        draft=False,
    )
    event.repository.create_pull.return_value.enable_automerge.assert_called_once_with(
        merge_method="SQUASH"
    )


def test_create_pr_no_commits(event):
    """
    This test case tests the create_branch_handler function when there are no commits between the new branch and the
    default branch. It checks that the function handles this situation correctly by not creating a pull request.
    """
    event.repository.create_pull.side_effect = GithubException(
        422, message="No commits between 'master' and 'issue-42'"
    )
    create_branch_handler(event)


def test_create_pr_other_exceptions(event):
    """
    This test case tests the create_branch_handler function when an exception other than 'No commits between master and
    feature' is raised. It checks that the function raises the exception as expected.
    """
    event.repository.create_pull.side_effect = GithubException(
        422, message="Other exception"
    )
    with pytest.raises(GithubException):
        create_branch_handler(event)


def test_enable_just_automerge_on_existing_pr(event):
    """
    This test case tests the create_branch_handler function when a pull request already exists for the new branch.
    It checks that the function enables auto-merge for the existing pull request and does not create a new pull request.
    """
    existing_pr = Mock()
    event.repository.get_pulls.return_value = [existing_pr]
    create_branch_handler(event)
    event.repository.create_pull.assert_not_called()
    existing_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")
