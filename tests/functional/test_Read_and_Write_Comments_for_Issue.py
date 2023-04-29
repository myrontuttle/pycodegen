"""Read and Write Comments for Issue feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen import todo
from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue_num = 5


@scenario(
    "../features/Read_and_Write_Comments_for_Issue.feature",
    "Read Comments for Issue",
)
def test_read_comments_for_issue():
    """Read Comments for Issue."""


@given("an open issue in GitHub")
def open_github_issue():
    """an open issue in GitHub."""


@when("the coder opens the issue")
def open_issue():
    """the coder opens the issue."""


@then("they read all comments for that issue")
def read_comments_for_issue():
    """they read all comments for that issue."""
    github_repo = todo.get_repo(repo_owner, test_repo)
    issue = github_repo.get_issue(test_issue_num)
    comments = todo.get_issue_comments(issue)
    assert comments[0] == "Imagine some great dev advice here."


@then("they comment with any questions they have about the issue")
def comment_with_questions():
    """they comment with any questions they have about the issue."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue_num)
    github_repo = todo.get_repo(repo_owner, test_repo)
    issue = github_repo.get_issue(test_issue_num)
    comments = todo.get_issue_comments(issue)
    assert len(comments) > 1
    # Pause here to review written comment
    todo.delete_last_issue_comment(issue)
