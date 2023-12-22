import logging

from github import GithubException

logger = logging.getLogger(__name__)


def get_existing_pr(repo, head):
    """
    Returns an existing PR if it exists.
    :param repo: The Repository to get the PR from.
    :param head: The branch to check for an existing PR.
    :return: Exists PR or None.
    """
    return next(
        iter(repo.get_pulls(state="open", head=head)), None
    )


def create_pr(repo, branch):
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
        if (
            ghe.message
            == f"No commits between '{repo.default_branch}' and '{branch}'"
        ):
            logger.warning(
                "No commits between '%s' and '%s'", repo.default_branch, branch
            )
        else:
            raise


def enable_auto_merge(pr):
    """
    Enables auto merge for the given PR.
    :param pr: The PR to enable auto merge for.
    """
    pr.enable_automerge(merge_method="SQUASH")


def get_or_create_pr(repo, branch):
    """
    Get a existing PR or create a new one if none exists
    :param repo:
    :param branch:
    :return: The created or recovered PR or None if no commits between 'master' and 'branch'
    """
    if pr := get_existing_pr(repo, f"{repo.owner.login}:{branch}"):
        print(
            f"PR already exists for '{repo.owner.login}:{branch}' into '{repo.default_branch} (PR#{pr.number})'"
        )
        logger.info(
            "-" * 50 + "PR already exists for '%s:%s' into '%s'",
            repo.owner.login,
            branch,
            repo.default_branch,
        )
    else:
        pr = create_pr(repo, branch)
    return pr
