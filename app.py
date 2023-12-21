import logging
import sys

import sentry_sdk
from flask import Flask, request
from github import PullRequest
from githubapp.events import CreateBranchEvent
from githubapp.webhook_handler import WebhookHandler, webhook_handler

# Create a Flask app
app = Flask("Pull Request Generator")
sentry_sdk.init(
    "https://575b73d4722bd4f8cc8bafb0274e4480@o305287.ingest.sentry.io/4506434483453952"
)

logging.basicConfig(
    stream=sys.stdout,
    format="%(levelname)s:%(module)s:%(funcName)s:%(message)s",
    level=logging.INFO,
)


@webhook_handler(CreateBranchEvent)
def create_branch_handler(event: CreateBranchEvent):
    repo = event.repository
    logging.info(f"Branch {event.ref} created in {repo.full_name}")
    if existing_prs := repo.get_pulls(state="open", head=event.ref):
        logging.info(
            "-" * 50
            + f"PR already exists for '{event.ref}' into '{repo.default_branch}'"
        )
        pr = existing_prs[0]
    else:
        logging.info(
            "-" * 50 + f"Creating PR for '{event.ref}' into '{repo.default_branch}'"
        )
        pr = repo.create_pull(
            repo.default_branch,
            event.ref,
            title=event.ref,
            body="PR automatically created",
            draft=False,
        )
    pr.enable_automerge(merge_method="SQUASH")


@app.route("/", methods=["GET"])
def root():
    return WebhookHandler.root("Pull Request Generator")()


@app.route("/", methods=["POST"])
def webhook():
    headers = dict(request.headers)
    body = request.json
    WebhookHandler.handle(headers, body)
    return "OK"
