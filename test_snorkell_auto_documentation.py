import unittest
from unittest.mock import Mock

import pytest
from pr_handler import enable_auto_merge, get_or_create_pr

from app import create_branch_handler


class TestSnorkellAutoDocumentation(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.repository.default_branch = "master"
        self.repository.full_name = "heitorpolidoro/pull-request-generator"
        self.repository.get_pulls.return_value = []

        self.branch = "issue-42"

        self.event = Mock()
        self.event.repository = self.repository
        self.event.ref = self.branch

    def test_create_pr(self):
        create_branch_handler(self.event)
        self.event.repository.create_pull.assert_called_once()
        self.event.repository.create_pull.return_value.enable_automerge.assert_called_once_with(merge_method="SQUASH")

    def test_create_pr_no_commits(self):
        self.event.repository.create_pull.side_effect = Exception("No commits between 'master' and 'issue-42'")
        with pytest.raises(Exception):
            create_branch_handler(self.event)

    def test_enable_just_automerge_on_existing_pr(self):
        existing_pr = Mock()
        self.event.repository.get_pulls.return_value = [existing_pr]
        create_branch_handler(self.event)
        self.event.repository.create_pull.assert_not_called()
        existing_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")
