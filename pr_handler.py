import logging

from github import GithubException

logger = logging.getLogger(__name__)


def log_branch_creation(repo, event):
    logger.info(
        "Branch %s:%s created in %s", repo.owner.login, event.ref, repo.full_name
    )


def get_existing_pr(repo, event):
    return next(
        iter(repo.get_pulls(state="open", head=f"{repo.owner.login}:{event.ref}")), None
    )


def create_pr(repo, event):
    try:
        pr = repo.create_pull(
            repo.default_branch,
            event.ref,
            title=event.ref,
            body="PR automatically created",
            draft=False,
        )
    except GithubException as ghe:
        if (
            ghe.message
            == f"No commits between '{repo.default_branch}' and '{event.ref}'"
        ):
            logger.warning(
                "No commits between '%s' and '%s'", repo.default_branch, event.ref
            )
        else:
            raise
    return pr


def enable_auto_merge(pr):
    pr.enable_automerge(merge_method="SQUASH")
