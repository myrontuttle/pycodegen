from typing import Optional

import logging
import os

from github import Github
from github.Issue import Issue
from github.Repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def get_gh_token_from_env() -> Optional[str]:
    """Returns Github Token if available as environment variable."""
    if "GH_TOKEN" not in os.environ:
        logger.critical(
            "GH_TOKEN does not exist as environment variable.",
        )
        logger.debug(os.environ)
    return os.getenv("GH_TOKEN")


def get_repo(repo_owner: str, repo_name: str) -> Optional[Repository]:
    token = get_gh_token_from_env()
    if not token:
        return None

    g = Github(token)
    return g.get_repo(f"{repo_owner}/{repo_name}")


def get_next_issue(repo_owner: str, repo_name: str) -> Optional[Issue]:
    """
    Get the next task for repo

    Parameters
    ----------
    repo_owner
    repo_name

    Returns
    -------
    GitHub Issue representing the next task to do (None if no more issues)
    """
    repo = get_repo(repo_owner, repo_name)
    if not repo:
        return None
    open_issues = repo.get_issues(
        state="open", direction="asc", creator=repo_owner
    )
    if not open_issues:
        logger.info(f"No open issues for repo: {repo_owner}/{repo_name}")
        return None
    for issue in open_issues:
        issue.edit(state="open")
    # TODO: Add logic to determine which open issue is highest priority
    # Currently getting the oldest open issue
    next_open_issue = open_issues[0]
    return next_open_issue


def issue_title_to_branch_name(
    repo_owner: str, repo_name: str, issue: Issue
) -> str:
    """
    Provide a branch name based on naming conventions for an issue
    Parameters
    ----------
    repo_owner
    repo_name
    issue

    Returns
    -------
    branch_name (str)
    """
    repo = get_repo(repo_owner, repo_name)
    if repo.get_label("enhancement") in issue.labels:
        branch_name = "feat"
    elif repo.get_label("bug") in issue.labels:
        branch_name = "bug"
    else:
        branch_name = "chore"
    branch_name += f"/{issue.number}/"
    branch_name += issue.title.replace(" ", "-")
    return branch_name
