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


def get_next_task(reponame: str) -> Optional[Issue]:
    """
    Get the next task for repo

    Parameters
    ----------
    reponame (owner/repo)

    Returns
    -------
    GitHub Issue representing the next task to do (None if no more issues)
    """
    token = get_gh_token_from_env()
    if not token:
        return None

    g = Github(token)
    repo = g.get_repo(reponame)
    open_issues = repo.get_issues(state="open")
    if not open_issues:
        logger.info(f"No open issues for repo: {reponame}")
        return None

    # TODO: Add logic to determine which open issue is highest priority
    return open_issues[0]
