import os
from pathlib import Path

from pycodegen import sc, todo
from pycodegen.coder import Coder

work_dir = Path("C:\\Users\\myron\\PycharmProjects")
host = "https://github.com"
owner = "myrontuttle"
test_repo = "test_project"
test_file = "test_file.txt"


def test_clone_checkout_and_commit() -> None:
    """
    Test that we can clone, check out a branch, and commit to it.
    """
    repo = sc.use_repo(work_dir, test_repo, owner)
    assert repo

    branch_name = "chore/test_branch"
    sc.use_branch(repo, branch_name)
    assert branch_name == repo.active_branch.name

    test_file_path = work_dir.joinpath(test_repo).joinpath(test_file)
    if os.path.exists(test_file_path):
        with open(test_file_path, "a") as fp:
            fp.write("This is another line\n")
    else:
        with open(test_file_path, "w") as fp:
            fp.write("This is the first line\n")
    sc.add_and_commit(repo, [test_file], "chore:Test commit")
    assert not repo.is_dirty(untracked_files=True)

    sc.safe_merge(repo, branch_name)
    assert repo.active_branch.name == "main"

    sc.push_to_origin(repo)


def test_get_next_issue() -> None:
    """
    Test that we can get the next task to do
    """
    repo_owner = "myrontuttle"
    repo_name = "pycodegen"
    next_issue = todo.get_next_issue(f"{repo_owner}/{repo_name}")
    assert next_issue and next_issue.title == "Pull issue from GitHub"


def test_code_start() -> None:
    """
    Test starting coding
    """
    coder = Coder(owner, test_repo)
    coder.open_next_issue()
    assert sc.get_active_branch_name(coder.repo) == "feat/3/Test-an-issue"
