from typing import Optional

import logging
import os
import subprocess
from pathlib import Path

import click
from github.Issue import Issue

from pycodegen import sc, tester, todo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


class Coder:
    """
    Coder Class
    """

    work_dir = Path("C:\\Users\\myron\\PycharmProjects")
    host = "https://github.com"

    def __init__(self, owner_name: str, repo_name: str):
        """
        Initializes a coder on a repo
        Parameters
        ----------
        owner_name
        repo_name
        """
        self.repo_owner = owner_name
        self.repo_name = repo_name
        self.repo = sc.use_repo(self.work_dir, self.repo_name, self.repo_owner)
        self.repo_path = self.work_dir.joinpath(self.repo_name)
        tester.create_bdd_dirs(self.repo_path)

        venv_path = self.repo_path.joinpath(".venv")
        # TODO: Use appropriate python version in following subprocesses
        if not venv_path.exists():
            os.chdir(self.repo_path)
            cp_setup = subprocess.run(
                [
                    "pdm",
                    "venv",
                    "create",
                    "3.9",
                    "-v",
                ],
                capture_output=True,
            )
            cp_setup2 = subprocess.run(
                [
                    "pdm",
                    "venv",
                    "activate",
                    "in-project",
                ],
                capture_output=True,
                shell=True,
            )  # nosec B602
            subprocess.run(
                [
                    "pdm",
                    "use",
                    "3.9",
                    "-i",
                    "-f",
                    "-vv",
                ],
                capture_output=True,
            )
            subprocess.run(
                [
                    "make",
                    "install",
                ],
                capture_output=True,
            )
            if cp_setup2.returncode == 0:
                # May be too much to push to logs
                logger.info(cp_setup.stdout)
            else:
                logger.error(cp_setup.stderr)

    def open_issue(self, issue_num: Optional[int]) -> Optional[Issue]:
        """
        Open an issue to work on. Either a specific issue or next available
        Parameters
        ----------
        issue_num

        Returns
        -------
        The issue we're working on if available
        """
        if issue_num:
            issue = todo.get_issue(self.repo_owner, self.repo_name, issue_num)
        else:
            issue = todo.get_next_issue(self.repo_owner, self.repo_name)
        if not issue:
            return None

        # Checkout git branch
        branch_name = todo.issue_title_to_branch_name(
            self.repo_owner, self.repo_name, issue
        )
        sc.use_branch(self.repo, branch_name)

        # Create functional test
        if branch_name.startswith(todo.feature_prepend):
            feature_path = tester.create_feature(self.repo_path, issue)
            tester.create_step_defs(feature_path)

        return issue

    def complete_active_issue(self, commit_msg: str):
        """
        Formats, commits, merge, and push any work on active branch
        """
        os.chdir(self.repo_path)
        cp_format = subprocess.run(
            [
                "make",
                "format",
            ],
            capture_output=True,
        )
        if cp_format.returncode == 0:
            # May be too much to push to logs
            logger.info(cp_format.stdout)
        else:
            logger.error(cp_format.stderr)
            return
        branch_name = sc.get_active_branch_name(self.repo)
        # TODO: Make commit msg based on branch_name and work done
        issue_num = todo.issue_num_from_branch_name(branch_name)
        if issue_num:
            commit_msg = "Fixes #" + str(issue_num) + ". " + commit_msg
        git_response_code = sc.add_and_commit(self.repo, ["."], commit_msg)
        if git_response_code != 0:
            return
        git_response_code = sc.safe_merge(self.repo, branch_name)
        if git_response_code != 0:
            return
        sc.push_to_origin(self.repo)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def code():
    pass


@code.command()
@click.argument("repo_owner")
@click.argument("repo_name")
@click.option("-i", "--issue_num", type=int)
def start(repo_owner: str, repo_name: str, issue_num: Optional[int]) -> None:
    coder = Coder(repo_owner, repo_name)
    coder.open_issue(issue_num)


@code.command()
@click.argument("repo_owner")
@click.argument("repo_name")
@click.argument("commit_msg")
def stop(repo_owner: str, repo_name: str, commit_msg: str) -> None:
    coder = Coder(repo_owner, repo_name)
    coder.complete_active_issue(commit_msg)


if __name__ == "__main__":
    code()
