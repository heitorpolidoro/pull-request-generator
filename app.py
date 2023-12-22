"""
This file contains the main application logic for the Pull Request Generator,
including a webhook handler for creating pull requests when new branches are created.
"""
import logging
import sys

import sentry_sdk
from flask import Flask, request
from githubapp import webhook_handler
from githubapp.events import CreateBranchEvent

from pr_handler import (
    create_pr,
    enable_auto_merge,
    get_existing_pr,
    log_branch_creation,
)

# Create a Flask app
app = Flask("Pull Request Generator")
sentry_sdk.init(
    "https://575b73d4722bd4f8cc8bafb0274e4480@o305287.ingest.sentry.io/4506434483453952"
)
logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    format="%(levelname)s:%(module)s:%(funcName)s:%(message)s",
    level=logging.INFO,
)


@webhook_handler.webhook_handler(CreateBranchEvent)
def create_branch_handler(event: CreateBranchEvent):
    """
    This function is a webhook handler that creates a pull request when a new branch is created.
    It takes a CreateBranchEvent object as a parameter, which contains information about the new branch.
    If a pull request already exists for the new branch, the function enables auto-merge for the pull request.
    Otherwise, it creates a new pull request and enables auto-merge for it.
    """
    repo = event.repository
    # Log branch creation
    log_branch_creation(repo, event)
    if pr := get_existing_pr(repo, event):
        print(
            f"PR already exists for '{repo.owner.login}:{event.ref}' into '{repo.default_branch} (PR#{pr.number})'"
        )
        logger.info(
            "-" * 50 + "PR already exists for '%s:%s' into '%s'",
            repo.owner.login,
            event.ref,
            repo.default_branch,
        )
    else:
        pr = create_pr(repo, event)
    if pr:
        enable_auto_merge(pr)


@app.route("/", methods=["GET"])
def root():
    return webhook_handler.root("Pull Request Generator")()


@app.route("/", methods=["POST"])
def webhook():
    headers = dict(request.headers)
    body = request.json
    webhook_handler.handle(headers, body)
    return "OK"
