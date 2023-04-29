from typing import List, Optional

import logging
import os

from github import Github
from github.GithubException import GithubException
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.Repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

feature_branch_prefix = "feat"
feature_type = "feature"
bug_branch_prefix = "fix"
bug_type = "bug"
doc_branch_prefix = "docs"
docs_type = "docs"
chore_branch_prefix = "chore"
chore_type = "chore"


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

    Args:
        repo_owner
        repo_name

    Returns:
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


def get_issue(repo: Repository, issue_num: int) -> Optional[Issue]:
    """
    Get a specific task to do for repo

    Args:
        repo
        issue_num

    Returns:
        GitHub Issue representing the issue specified (None if no issue with
        that number)
    """
    if not repo:
        return None
    try:
        return repo.get_issue(issue_num)
    except GithubException as ge:
        logger.error(ge)
        return None


def get_issue_type(repo: Repository, issue: Issue) -> Optional[str]:
    """
    Determine the issue type from the labels

    Args:
        repo
        issue

    Returns:
        Issue type (str)
    """
    if issue.labels:
        if repo.get_label("enhancement") in issue.labels:
            return feature_type
        elif repo.get_label("bug") in issue.labels:
            return bug_type
        elif repo.get_label("documentation") in issue.labels:
            return docs_type
        else:
            return chore_type
    else:
        return None


def issue_title_to_branch_name(repo: Repository, issue: Issue) -> str:
    """
    Provide a branch name based on naming conventions for an issue
    Args:
        repo
        issue

    Returns:
        branch_name (str)
    """
    issue_type = get_issue_type(repo, issue)
    if issue_type == feature_type:
        branch_name = feature_branch_prefix
    elif issue_type == bug_type:
        branch_name = bug_branch_prefix
    elif issue_type == docs_type:
        branch_name = doc_branch_prefix
    else:
        branch_name = chore_branch_prefix
    branch_name += f"/{issue.number}/"
    branch_name += issue.title.replace(" ", "-")
    return branch_name


def issue_num_from_branch_name(branch_name: str) -> Optional[str]:
    """
    Parses the issue number from the branch name
    Args:
        branch_name

    Returns:
        Issue number
    """
    issue_split = branch_name.split("/")
    if issue_split[1]:
        try:
            issue_num = int(issue_split[1])
        except ValueError as ve:
            logger.warning(
                "Can't parse issue number from branch name: " + str(ve)
            )
            return None
        else:
            return str(issue_num)
    else:
        logger.warning("No issue number found in branch name.")
        return None


def issue_prefix_from_branch_name(branch_name: str) -> Optional[str]:
    """Returns the issue type from the branch name"""
    issue_split = branch_name.split("/")
    if issue_split[0]:
        return issue_split[0]
    else:
        logger.warning("No issue type found in branch name.")
    return None


def get_issue_type_from_prefix(issue_prefix: str) -> str:
    """Returns the issue type from the issue prefix"""
    if issue_prefix == feature_branch_prefix:
        return feature_type
    elif issue_prefix == bug_branch_prefix:
        return bug_type
    elif issue_prefix == doc_branch_prefix:
        return docs_type
    else:
        return chore_type


def get_issue_comments(issue: Issue) -> Optional[List[str]]:
    """Returns a list of comments for an issue"""
    if not issue:
        return None
    comments = [comment.body for comment in issue.get_comments()]
    return comments


def write_issue_comment(issue: Issue, comment: str) -> Optional[IssueComment]:
    """Writes a comment to an issue"""
    if not issue:
        return None
    return issue.create_comment(comment)


def delete_last_issue_comment(issue: Issue) -> Optional[IssueComment]:
    """Deletes the last comment on an issue"""
    if not issue:
        return None
    comments = issue.get_comments()
    if not comments:
        return None
    num_comments = comments.totalCount
    last_comment = comments[num_comments - 1]
    last_comment.delete()
    return last_comment
