from typing import List

import logging
from pathlib import Path

import git
from git import Repo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

github_host = "github.com"


def use_repo(work_dir: Path, repo_name: str, username: str) -> Repo:
    """
    Gets a reference to a repo if it exists locally, otherwise clones from
    GitHub
    Parameters
    ----------
    work_dir
    repo_name
    username

    Returns
    -------
    Repo
    """
    repo_path = work_dir.joinpath(repo_name)
    if repo_path.exists():
        try:
            repo = git.Repo(repo_path)
            return repo
        except git.exc.InvalidGitRepositoryError:
            logger.warning(f"No repo at {repo_path}. Initializing new repo.")
            repo = git.Repo.init(repo_path)
            return repo
    else:
        logger.info(f"Cloning repo into {repo_path}")
        repo_url = f"git@{github_host}:{username}/{repo_name}"
        try:
            repo = git.Repo.clone_from(repo_url, repo_path)
            return repo
        except git.exc.InvalidGitRepositoryError:
            logger.warning(f"No remote repo at {repo_url}")


def update_repo(repo: Repo) -> None:
    """
    Updates a repo from remote origin
    Parameters
    ----------
    repo

    Returns
    -------
    None
    """
    repo.remotes.origin.pull()
    # TODO: Add info to indicate status


def use_branch(repo: Repo, branch_name: str) -> None:
    """
    Creates branch_name if it doesn't exist and switches to it

    Parameters
    ----------
    repo
    branch_name

    Returns
    -------
    None
    """
    if branch_name not in repo.branches:
        repo.git.branch(branch_name)
    repo.git.checkout(branch_name)


def add_and_commit(repo: Repo, files: List[str], commit_msg: str) -> None:
    """
    Adds specified files and commits them to the current branch of the repo

    Parameters
    ----------
    repo
    files
    commit_msg

    Returns
    -------
    None
    """
    if files[0] == ".":
        repo.git.add(all=True)
    else:
        repo.index.add(files)
    repo.index.commit(commit_msg)


def safe_merge(repo: Repo, branch_name: str) -> None:
    """
    Safely merge branch_name into main

    Parameters
    ----------
    repo
    branch_name

    Returns
    -------
    None
    """
    if repo.active_branch.name != branch_name:
        use_branch(repo, branch_name)
    repo.git.fetch()
    repo.git.rebase("origin/main")
    # TODO: Add error handling if conflicts with origin/main
    use_branch(repo, "main")
    repo.remotes.origin.pull()
    repo.git.merge(branch_name)
    # TODO: Add error handling if conflicts with branch


def push_to_origin(repo: Repo) -> None:
    """
    Pushes main to origin

    Parameters
    ----------
    repo

    Returns
    -------
    None
    """
    if repo.active_branch.name != "main":
        use_branch(repo, "main")
    repo.remotes.origin.push("main")
    # TODO: Get a response that can be tested. Tried PushInfo, but PyCharm
    # couldn't handle it.
