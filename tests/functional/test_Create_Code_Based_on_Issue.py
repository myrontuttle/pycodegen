"""Create code based on issue feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen import sc
from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue_num = 3
src_file_name = "issue.py"


@scenario(
    "../features/Create_Code_Based_on_Issue.feature",
    "Create Code from Issue",
)
def test_create_code_from_issue():
    """Create Code from Issue."""


@given("an open issue for a repo")
def get_open_issue():
    """an open issue for a repo."""
    coder = Coder(repo_owner, test_repo)
    rc = coder.open_issue(test_issue_num)
    assert rc == 0


@when("I provide the text of the issue and a file to add code to")
def issue_and_file():
    """I provide the text of the issue and a file to add code to."""
    coder = Coder(repo_owner, test_repo)
    rc = coder.start_coding()
    assert rc == 0


@then(
    "the program generates code based on that issue and that code contains "
    "a logger."
)
def check_code_generated():
    """the program generates code based on that issue and that code contains
    a logger."""
    coder = Coder(repo_owner, test_repo)
    src_path = coder.repo_path.joinpath("src", coder.repo_name, src_file_name)
    assert src_path.exists()
    with open(src_path, "r") as sp:
        contents = sp.read()
        assert contents
        assert contents.find("logger") != -1
    # Cleanup
    sc.undo_changes(coder.repo)
