"""Cleanup Branch When Done feature tests."""
import os

from pytest_bdd import given, scenario, then, when

from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue = 3
test_file = "test_file.txt"
test_branch = "feat/3/Test-an-issue"
test_commit_msg = "I'm done!"


@scenario("../features/Cleanup_Branch_When_Done.feature", "Delete branch")
def test_delete_branch():
    """Delete branch."""


@given("a branch other than main")
def open_a_branch():
    """a branch other than main."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue)


@when("work is completed for the issue that branch was opened for")
def complete_work():
    """work is completed for the issue that branch was opened for."""
    coder = Coder(repo_owner, test_repo)
    work_dir = Coder.work_dir
    test_file_path = work_dir.joinpath(test_repo).joinpath(test_file)
    if os.path.exists(test_file_path):
        with open(test_file_path, "a") as fp:
            fp.write("This is another line\n")
    else:
        with open(test_file_path, "w") as fp:
            fp.write("This is the first line\n")
    coder.complete_active_issue(test_commit_msg)


@then("the branch is deleted")
def check_for_deleted_branch():
    """the branch is deleted."""
    coder = Coder(repo_owner, test_repo)
    assert test_branch not in coder.repo.branches
