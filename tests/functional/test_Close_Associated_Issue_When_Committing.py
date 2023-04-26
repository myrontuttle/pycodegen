"""Close Associated Issue When Committing feature tests."""


from pytest_bdd import given, scenario, then, when

from pycodegen import sc
from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue = 3
test_commit_msg = "I'm done!"


@scenario(
    "../features/Close_Associated_Issue_When_Committing.feature",
    "Close Associated Issue",
)
def test_close_associated_issue():
    """Close Associated Issue."""


@given("the coder is working on an open branch")
def coder_working():
    """the coder is working on an open branch."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue)


@when("they complete the active issue")
def coding_complete():
    """they complete the active issue."""
    coder = Coder(repo_owner, test_repo)
    coder.finish_issue(test_commit_msg)


@then(
    'the commit message automatically includes "Fixes " and the number of '
    "the issue"
)
def check_commit_msg():
    """the commit message automatically includes "Fixes " and the number of
    the issue."""
    coder = Coder(repo_owner, test_repo)
    last_commit_msg = sc.get_last_commit_msg(coder.repo)
    assert last_commit_msg.startswith("Fixes #3")
