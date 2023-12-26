"""
This module contains functions for handling pull requests from GitHub webhooks.

It provides functions to get existing PRs, create new PRs, and handle errors from the GitHub API.
"""

# rest of module

import logging
from typing import Optional

from github import GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository

logger = logging.getLogger(__name__)


def get_existing_pr(repo: Repository, head: str) -> Optional[PullRequest]:
    """
    Returns an existing PR if it exists.
    :param repo: The Repository to get the PR from.
    :param head: The branch to check for an existing PR.
    :return: Exists PR or None.
    """
    return next(iter(repo.get_pulls(state="open", head=head)), None)


def create_pr(repo: Repository, branch: str) -> Optional[PullRequest]:
    """
    Creates a PR from the default branch to the given branch.
    :param repo: The Repository to create the PR in.
    :param branch:
    :return: Created PR or None.
    :raises: GithubException if and error occurs, except if the error is "No commits between 'master' and 'branch'"
    in that case ignores the exception and it returns None.
    """
    try:
        pr = repo.create_pull(
            repo.default_branch,
            branch,
            title=branch,
            body="PR automatically created",
            draft=False,
        )
        return pr
    except GithubException as ghe:
        if ghe.message == f"No commits between '{repo.default_branch}' and '{branch}'":
            logger.warning(
                "No commits between '%s' and '%s'", repo.default_branch, branch
            )
        else:
            raise
    return None


def enable_auto_merge(pr: PullRequest) -> None:
    """
    Enables auto merge for the given PR.
    This function takes a PullRequest object as a parameter and enables the auto merge feature for it.
    The merge method used is "SQUASH".
    :param pr: The PR to enable auto merge for.
    :return: None
    """
    Enables auto merge for the given PR.
    :param pr: The PR to enable auto merge for.
    """
    pr.enable_automerge(merge_method="SQUASH")


def get_or_create_pr(repository: Repository, branch: str) -> Optional[PullRequest]:
    """
    This function either retrieves an existing pull request (PR) or creates a new one if none exists.
    It takes a Repository object and a branch name as parameters.
    If a PR already exists for the given branch, it retrieves and returns the PR.
    If no PR exists, it creates a new PR for the branch.
    If there are no commits between the 'master' branch and the given branch, it returns None.
    :param repository: The Repository object to get or create the PR in.
    :param branch: The name of the branch to get or create a PR for.
    :return: The existing or newly created PR, or None if there are no commits between 'master' and the given branch.
    """
    if pr := get_existing_pr(repository, f"{repository.owner.login}:{branch}"):
        print(
            f"PR already exists for '{repository.owner.login}:{branch}' into "
            f"'{repository.default_branch} (PR#{pr.number})'"
        )
        logger.info(
            "-" * 50 + "PR already exists for '%s:%s' into '%s'",
            repository.owner.login,
            branch,
            repository.default_branch,
        )
    else:
        pr = create_pr(repository, branch)
    return pr
