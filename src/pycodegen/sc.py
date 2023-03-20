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


def get_active_branch_name(repo: Repo) -> str:
    return repo.active_branch.name


def add_and_commit(repo: Repo, files: List[str], commit_msg: str) -> int:
    """
    Adds specified files and commits them to the current branch of the repo

    Parameters
    ----------
    repo
    files
    commit_msg

    Returns
    -------
    Status Code
    """
    if files[0] == ".":
        repo.git.add(all=True)
    else:
        repo.index.add(files)
    try:
        repo.git.commit(m=commit_msg)
        # repo.index.commit(commit_msg)
    except git.exc.HookExecutionError as hee:
        logger.warning(
            f"Error executing hook.\n{str(hee)}\nTrying without "
            f"pre-commit."
        )
        try:
            repo.git.commit(m=commit_msg, no_verify=True)
        except git.exc.GitCommandError as gce:
            logger.warning("Git commit command error: " + str(gce))
            return 1
    except git.exc.GitCommandError as gce:
        logger.warning("Git commit command error: " + str(gce))
        return 1
    return 0


def safe_merge(repo: Repo, branch_name: str) -> int:
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
    try:
        repo.git.rebase("origin/main")
    except git.exc.GitCommandError as gce:
        logger.warning("Git commit command error: " + str(gce))
        return 1
    use_branch(repo, "main")
    repo.remotes.origin.pull()
    try:
        repo.git.merge(branch_name)
    except git.exc.GitCommandError as gce:
        logger.warning("Git commit command error: " + str(gce))
        return 1
    return 0


def push_to_origin(repo: Repo) -> int:
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
    try:
        repo.remotes.origin.push("main")
    except git.exc.GitCommandError as gce:
        logger.warning("Git commit command error: " + str(gce))
        return 1
    else:
        return 0


def get_last_commit_msg(repo: Repo) -> str:
    """
    Get the last commit message
    Parameters
    ----------
    repo

    Returns
    -------
    String of last commit message
    """
    head_commit = repo.head.commit
    return head_commit.message


def delete_branch(repo: Repo, branch_name: str) -> None:
    """
    Deletes the indicated branch
    Parameters
    ----------
    repo
    branch_name

    Returns
    -------
    None
    """
    try:
        repo.git.branch("-D", branch_name)
    except git.exc.GitCommandError as gce:
        logger.error("Git commit command error: " + str(gce))
