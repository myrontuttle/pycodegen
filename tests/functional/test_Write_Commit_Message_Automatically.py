"""Write Commit Message Automatically feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen import sc
from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue_num = 3


@scenario(
    "../features/Write_Commit_Message_Automatically.feature",
    "Automatic Commit Message",
)
def test_automatic_commit_message():
    """Automatic Commit Message."""


@given("a code change on a branch")
def code_change():
    """a code change on a branch."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue_num)


@when("that branch is added and committed")
def add_changes():
    """that branch is added and committed."""
    coder = Coder(repo_owner, test_repo)
    sc.add_files(coder.repo, ["."])


@then("a commit message is automatically created")
def check_commit_message():
    """a commit message is automatically created."""
    coder = Coder(repo_owner, test_repo)
    branch_name = sc.get_active_branch_name(coder.repo)
    # Fix any issues in the code that would prevent a commit before proceeding
    commit_msg = sc.generate_commit_msg(coder.repo, branch_name)
    assert commit_msg
    sc.use_branch(coder.repo, "main")
    sc.delete_branch(coder.repo, branch_name)
