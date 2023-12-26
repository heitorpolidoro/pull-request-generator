"""
This file contains the main application logic for the Pull Request Generator,
including a webhook handler for creating pull requests when new branches are created.
"""
import logging
import os
import sys

import sentry_sdk
from flask import Flask, request
from githubapp import webhook_handler
from githubapp.events import CreateBranchEvent

from pr_handler import enable_auto_merge, get_or_create_pr

app = Flask("Pull Request Generator")
app.__doc__ = "This is a Flask application for generating pull requests."

if sentry_dns := os.getenv("SENTRY_DNS"):  # pragma: no cover
    # Initialize Sentry SDK for error logging
    sentry_sdk.init(sentry_dns)

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    format="%(levelname)s:%(module)s:%(funcName)s:%(message)s",
    level=logging.INFO,
)


@webhook_handler.webhook_handler(CreateBranchEvent)
def create_branch_handler(event: CreateBranchEvent) -> None:
    """
    This function is a webhook handler that creates a pull request when a new branch is created.
    It takes a CreateBranchEvent object as a parameter, which contains information about the new branch.
    If a pull request already exists for the new branch, the function enables auto-merge for the pull request.
    Otherwise, it creates a new pull request and enables auto-merge for it.
    """
    repo = event.repository
    # Log branch creation
    logger.info(
        "Branch %s:%s created in %s", repo.owner.login, event.ref, repo.full_name
    )
    if pr := get_or_create_pr(event.repository, event.ref):
        enable_auto_merge(pr)


@app.route("/", methods=["GET"])
def root() -> str:
    """
    This function is the root of the application, it handles GET requests to the root URL ("/").
    It does not take any parameters and returns a string which is the response to the GET request.
    """
    This route displays the welcome screen of the application.
    It uses the root function of the webhook_handler to generate the welcome screen.
    """
    return webhook_handler.root(app.name)()


@app.route("/", methods=["POST"])
def webhook() -> str:
    """
    This route is the endpoint that receives the GitHub webhook call.
    It handles the headers and body of the request, and passes them to the webhook_handler for processing.
    """
    headers = dict(request.headers)
    body = request.json
    webhook_handler.handle(headers, body)
    return "OK"
