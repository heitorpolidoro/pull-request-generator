import logging
import os

from github import Github
from githubapp import CreateBranchEvent, Flask
from githubapp.Event import Event

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.INFO)


# Create a Flask app
app = Flask("PR Creator")

logging.basicConfig(
    format="%(levelname)s:%(module)s:%(funcName)s:%(message)s", level=logging.INFO
)


@app.CreateBranch
def create_branch_handler(event: CreateBranchEvent):
    repo = event.repository
    logging.info(f"Branch {event.ref} created in {repo.full_name}")
    logging.info("-" * 50 + f"Creating PR for {event.ref} branch {repo.default_branch}")
    repo.create_pull(
        repo.default_branch,
        event.ref,
        title=event.ref,
        body="PR automatically created",
        draft=False,
    )
