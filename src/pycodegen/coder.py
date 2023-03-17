from typing import Optional

import logging
import os
import subprocess
from pathlib import Path

import click

from pycodegen import sc, todo

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
    owner = "myrontuttle"

    def __init__(self, repo_name: str):
        """
        Initializes a coder on a repo
        Parameters
        ----------
        repo_name
        """
        self.repo = sc.use_repo(self.work_dir, repo_name, self.owner)
        self.repo_path = self.work_dir.joinpath(repo_name)
        venv_path = self.repo_path.joinpath(".venv")
        if not venv_path.exists():
            os.chdir(self.repo_path)
            cp_setup = subprocess.run(
                [
                    "make",
                    "install",
                ],
                capture_output=True,
            )
            if cp_setup.returncode == 0:
                # May be too much to push to logs
                logger.info(cp_setup.stdout)
            else:
                logger.error(cp_setup.stderr)

    def open_next_issue(self) -> Optional[str]:
        repo_name = self.repo.__str__()
        next_issue = todo.get_next_issue(repo_name)
        if not next_issue:
            return None
        sc.use_branch(self.repo, todo.issue_title_to_branch_name(next_issue))
        return next_issue.body

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
        branch_name = sc.get_active_branch_name(self.repo)
        # TODO: Make commit msg based on branch_name and work done
        sc.add_and_commit(self.repo, ["."], commit_msg)
        sc.safe_merge(self.repo, branch_name)
        sc.push_to_origin(self.repo)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def code():
    pass


@code.command()
@click.argument("repo_name")
def start(repo_name: str) -> None:
    coder = Coder(repo_name)
    coder.open_next_issue()


@code.command()
@click.argument("repo_name")
@click.argument("commit_msg")
def stop(repo_name: str, commit_msg: str) -> None:
    coder = Coder(repo_name)
    coder.complete_active_issue(commit_msg)


if __name__ == "__main__":
    code()
