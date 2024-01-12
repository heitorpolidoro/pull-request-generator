"""
This file contains the main application logic for the Pull Request Generator,
including a webhook handler for creating pull requests when new branches are created.
"""
import logging
import os
import sys

import sentry_sdk
from flask import Flask
from githubapp import webhook_handler
from githubapp.events import CreateBranchEvent

from pr_handler import enable_auto_merge, get_or_create_pr

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    format="%(levelname)s:%(module)s:%(funcName)s:%(message)s",
    level=logging.INFO,
)


def sentry_init():  # pragma: no cover
    """Initialize sentry only if SENTRY_DSN is present"""
    if sentry_dns := os.getenv("SENTRY_DSN"):
        # Initialize Sentry SDK for error logging
        sentry_sdk.init(
            dsn=sentry_dns,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0,
        )
        logger.info("Sentry initialized")


app = Flask("Pull Request Generator")
__version__ = "0.1"
sentry_init()
webhook_handler.handle_with_flask(
    app, version=__version__, versions_to_show=["github-app-handler"]
)


@webhook_handler.webhook_handler(CreateBranchEvent)
def create_branch_handler(event: CreateBranchEvent) -> None:
    """
    This function is a webhook handler that creates a pull request when a new branch is created.
    It takes a CreateBranchEvent object as a parameter, which contains information about the new branch.
    If a pull request already exists for the new branch, the function enables auto-merge for the pull request.
    Otherwise, it creates a new pull request and enables auto-merge for it.
    """
    repository = event.repository
    branch = event.ref
    # Log branch creation
    logger.info(
        "Branch %s:%s created in %s",
        repository.owner.login,
        branch,
        repository.full_name,
    )
    if pr := get_or_create_pr(repository, branch):
        enable_auto_merge(pr)
