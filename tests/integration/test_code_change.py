import os
from pathlib import Path

from pycodegen import todo, vc

work_dir = Path("C:\\Users\\myron\\PycharmProjects")
host = "https://github.com"
owner = "myrontuttle"
test_repo = "test_project"
test_file = "test_file.txt"


def test_clone_checkout_and_commit() -> None:
    """
    Test that we can clone, check out a branch, and commit to it.
    """
    repo = vc.use_repo(work_dir, test_repo, owner)
    assert repo

    branch_name = "chore/test_branch"
    vc.use_branch(repo, branch_name)
    assert branch_name == repo.active_branch.name

    test_file_path = work_dir.joinpath(test_repo).joinpath(test_file)
    if os.path.exists(test_file_path):
        with open(test_file_path, "a") as fp:
            fp.write("This is another line\n")
    else:
        with open(test_file_path, "w") as fp:
            fp.write("This is the first line\n")
    vc.add_and_commit(repo, [test_file], "chore:Test commit")
    assert not repo.is_dirty(untracked_files=True)

    vc.safe_merge(repo, branch_name)
    assert repo.active_branch.name == "main"

    vc.push_to_origin(repo)


def test_get_next_task() -> None:
    """
    Test that we can get the next task to do
    """
    reponame = "myrontuttle/pycodegen"
    next_task = todo.get_next_task(reponame)
    assert next_task and next_task.title == "Pull issue from GitHub"
