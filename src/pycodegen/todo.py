from typing import Optional

import logging
import os

from github import Github
from github.Issue import Issue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

github_host = "github.com"
github_user = "myrontuttle"


def get_gh_token_from_env() -> Optional[str]:
    """Returns Github Token if available as environment variable."""
    if "GH_TOKEN" not in os.environ:
        logger.critical(
            "GH_TOKEN does not exist as environment variable.",
        )
        logger.debug(os.environ)
    return os.getenv("GH_TOKEN")


def get_next_issue(repo_name: str) -> Optional[Issue]:
    """
    Get the next task for repo

    Parameters
    ----------
    repo_name (owner/repo)

    Returns
    -------
    GitHub Issue representing the next task to do (None if no more issues)
    """
    token = get_gh_token_from_env()
    if not token:
        return None

    g = Github(token)
    repo = g.get_repo(repo_name)
    open_issues = repo.get_issues(state="open")
    if not open_issues:
        logger.info(f"No open issues for repo: {repo_name}")
        return None

    # TODO: Add logic to determine which open issue is highest priority
    return open_issues[0]


def issue_title_to_branch_name(issue: Issue) -> str:
    """
    Provide a branch name based on naming conventions for an issue
    Parameters
    ----------
    issue

    Returns
    -------
    branch_name (str)
    """
    if "enhancement" in issue.labels:
        branch_name = "feat"
    elif "bug" in issue.labels:
        branch_name = "bug"
    else:
        branch_name = "chore"
    branch_name += f"/{issue.id}/"
    branch_name += issue.title.replace(" ", "-")
    return branch_name
