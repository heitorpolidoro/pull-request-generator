import logging

from flask import Flask, request
from githubapp.events import CreateBranchEvent
from githubapp.webhook_handler import webhook_handler, WebhookHandler

# Create a Flask app
app = Flask("Pull Request Generator")

logging.basicConfig(
    format="%(levelname)s:%(module)s:%(funcName)s:%(message)s", level=logging.INFO
)


@webhook_handler(CreateBranchEvent)
def create_branch_handler(event: CreateBranchEvent):
    repo = event.repository
    logging.info(f"Branch {event.ref} created in {repo.full_name}")
    logging.info("-" * 50 + f"Creating PR for {event.ref} branch {repo.default_branch}")
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
