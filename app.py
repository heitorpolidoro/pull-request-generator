import logging
import sys

import sentry_sdk
from flask import Flask, request
from github import PullRequest
from github.Repository import Repository
from githubapp import webhook_handler
from githubapp.events import CreateBranchEvent

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
    repo = event.repository
    print(f"Branch {repo.owner.login}:{event.ref} created in {repo.full_name}")
    logger.info(f"Branch {repo.owner.login}:{event.ref} created in {repo.full_name}")
    if pr := next(
        iter(repo.get_pulls(state="open", head=f"{repo.owner.login}:{event.ref}")), None
    ):
        print(
            f"PR already exists for '{repo.owner.login}:{event.ref}' into '{repo.default_branch} (PR#{pr.number})'"
        )
        logger.info(
            "-" * 50
            + f"PR already exists for '{repo.owner.login}:{event.ref}' into '{repo.default_branch}'"
        )
    else:
        print(
            f"Creating PR for '{repo.owner.login}:{event.ref}' into '{repo.default_branch}'"
        )
        logger.info(
            "-" * 50
            + f"Creating PR for '{repo.owner.login}:{event.ref}' into '{repo.default_branch}'"
        )
        pr = repo.create_pull(
            repo.default_branch,
            event.ref,
            title=event.ref,
            body="PR automatically created",
            draft=False,
        )
        print(
            f"PR for '{repo.owner.login}:{event.ref}' into '{repo.default_branch} created"
        )
    print(f"Enabling automerge for PR#{pr.number}")
    pr.enable_automerge(merge_method="SQUASH")
    print(f"Automerge for PR#{pr.number} enabled")


@app.route("/", methods=["GET"])
def root():
    return webhook_handler.root("Pull Request Generator")()


@app.route("/", methods=["POST"])
def webhook():
    headers = dict(request.headers)
    body = request.json
    webhook_handler.handle(headers, body)
    return "OK"
