"""Split Issue Open and Coding Start feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen import sc
from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue_num = 5


@scenario(
    "../features/Split_Issue_Open_and_Coding_Start.feature", "Just Open Issue"
)
def test_just_open_issue():
    """Just Open Issue."""


@scenario(
    "../features/Split_Issue_Open_and_Coding_Start.feature", "Start Coding"
)
def test_start_coding():
    """Start Coding."""


@given("a new feature")
def a_new_feature():
    """a new feature."""


@given("a quick fix")
def a_fix():
    """a quick fix."""


@when("I ask the coder to open the issue")
def open_issue():
    """I ask the coder to open the issue."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue_num)


@when("I ask the coder to start coding")
def start_coding():
    """I ask the coder to start coding."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue_num)


@then("it creates tests and source code")
def check_tests_and_source_code_created():
    """it creates tests and source code."""
    coder = Coder(repo_owner, test_repo)
    response_code = coder.start_coding()
    assert response_code == 0
    sc.undo_changes(coder.repo)


@then("it just creates the branch")
def check_branch_created():
    """it just creates the branch."""
    coder = Coder(repo_owner, test_repo)
    assert sc.get_active_branch_name(coder.repo) == "feat/3/Test-an-issue"
    sc.undo_changes(coder.repo)
