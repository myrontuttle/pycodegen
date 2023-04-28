from typing import List

import logging
import re
from pathlib import Path

import git
from git import Repo

from pycodegen import llm, todo

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


def generate_commit_msg(repo: Repo, branch_name: str) -> str:
    """
    Generates a commit message based on the changes in the index (staging)
    of the provided repo. Run after adding changes to index (e.g. git add .)
    Args:
        repo
        branch_name

    Returns:
        Commit message as a string
    """
    # Set the --no-pager option for the git command so that we get everything
    repo.config_writer().set_value("core", "pager", "")

    # Generate a patch from the staged changes
    diff = repo.git.diff(
        "--cached",
    )

    commit_limit = 60
    issue_num = todo.issue_num_from_branch_name(branch_name)
    issue_prefix = todo.issue_prefix_from_branch_name(branch_name)
    if issue_num:
        commit_limit -= 10
    if issue_prefix:
        commit_limit -= 5

    prompt = (
        f"Write a git commit message for the following change. Limit "
        f"the message to just a one-line summary of less "
        f"then {commit_limit} characters.\n\n"
    )
    messages = llm.prompt_to_messages(prompt + diff)
    # Simple case. No summarizing needed.
    token_count = llm.num_tokens_from_messages(messages)
    if token_count <= llm.CH_MAX_TOKENS:
        result = llm.respond(messages)
        commit_msg = add_commit_message_info(result, issue_prefix, issue_num)
        return commit_msg
    # Otherwise, summarize the diff
    summaries = summarize(diff)
    summary_string = "\n".join(summaries)
    summary_message = llm.prompt_to_messages(prompt + summary_string)
    while True:
        if llm.num_tokens_from_messages(summary_message) <= llm.CH_MAX_TOKENS:
            break
        # Summarize the summary
        summaries = summarize(summary_string)
        summary_string = "\n".join(summaries)
        summary_message = llm.prompt_to_messages(prompt + summary_string)

    commit_msg = llm.respond(summary_message)
    commit_msg = add_commit_message_info(commit_msg, issue_prefix, issue_num)
    commit_msg = commit_msg + "\n\n" + "\n".join(summaries)
    return commit_msg


def add_commit_message_info(
    commit_msg: str, issue_prefix="", issue_num=""
) -> str:
    """
    Adds issue prefix and number to the commit message
    Args:
        commit_msg
        issue_prefix
        issue_num

    Returns:
        Commit message with issue type and number
    """
    if issue_num:
        commit_msg = commit_msg + " Fixes #" + str(issue_num)
    if issue_prefix:
        # Remove issue type from commit message if it's already there
        if commit_msg.find(": ") != -1:
            commit_msg = commit_msg[commit_msg.find(": ") + 2 :]
        # Add issue type from branch name
        commit_msg = issue_prefix + ": " + commit_msg
    return commit_msg


def summarize(text: str, split_re=None) -> List[str]:
    """Summarize a single diff or set of diff summaries"""
    if split_re is None:
        split_re = [
            r"^(diff )",  # First try to split by diff
            "^$",  # Then try blank line
            "\n",  # Then try newline
        ]
    prompt = "Summarize the following: "
    query = prompt + text
    query_message = llm.prompt_to_messages(query)
    token_count = llm.num_tokens_from_messages(query_message)

    if token_count <= llm.CH_MAX_TOKENS:
        return [llm.respond(query_message)]

    summaries = []
    parts = re.split(split_re[0], text, flags=re.MULTILINE)
    combined_parts = []
    # Now go back through and put the split string back together with the next
    # thing
    for part in parts:
        if re.match(split_re[0], part) or not combined_parts:
            combined_parts.append(part)
        else:
            combined_parts[-1] += part
    parts = combined_parts

    chunk = [parts[0]]
    chunk_token_count = llm.num_tokens_from_messages(
        llm.prompt_to_messages(parts[0])
    )
    for part in parts[1:]:
        part_token_count = llm.num_tokens_from_messages(
            llm.prompt_to_messages(part)
        )
        # print(f">>> {split_re[0]!r}",
        #      chunk_token_count,
        #      len(chunk),
        #      part_token_count,
        #      max_token_count[args.model])

        if chunk_token_count + part_token_count >= llm.CH_MAX_TOKENS:
            text = "".join(chunk)
            text_message = llm.prompt_to_messages(text)
            chunk = []
            if llm.num_tokens_from_messages(text_message) > llm.CH_MAX_TOKENS:
                # Need to split using a different regex
                summaries.extend(summarize(text, split_re=split_re[1:]))
            else:
                summaries.append(llm.complete_prompt(prompt + text))
            chunk_token_count = sum(
                llm.num_tokens_from_messages(llm.prompt_to_messages(c))
                for c in chunk
            )
        chunk.append(part)
        chunk_token_count += part_token_count
    return summaries


def add_files(repo: Repo, files: List[str]) -> None:
    """
    Adds specified files to the repo index/staging

    Parameters
    ----------
    repo
    files

    Returns
    -------
    Status Code
    """
    # Stage changes
    if files[0] == ".":
        repo.git.add(all=True)
    else:
        repo.index.add(files)


def commit(repo: Repo, commit_msg: str) -> int:
    """
    Commits changes to the current branch of the repo

    Parameters
    ----------
    repo
    commit_msg

    Returns
    -------
    Status Code
    """
    # Commit changes
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
