"""Create code based on issue feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen import sc
from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue_num = 3
files_created = []


@scenario(
    "../features/Create_Code_Based_on_Issue.feature",
    "Create Code " "from Issue",
)
def test_create_code_from_issue():
    """Create Code from Issue."""


@given("an open issue for a repo")
def get_open_issue():
    """an open issue for a repo."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue_num)
    return test_issue_num


@when("I provide the text of the issue and a file to add code to")
def issue_and_file():
    """I provide the text of the issue and a file to add code to."""
    coder = Coder(repo_owner, test_repo)
    file_name = coder.recommend_filename(test_issue_num)
    coder.write_src_code(test_issue_num, file_name)
    files_created.append(file_name)


@then(
    "the program generates code based on that issue and that code contains "
    "a logger."
)
def check_code_generated():
    """the program generates code based on that issue and that code contains
    a logger."""
    coder = Coder(repo_owner, test_repo)
    test_file_path = (
        coder.repo_path.joinpath("src")
        .joinpath(coder.repo_name)
        .joinpath(files_created[0])
    )
    assert test_file_path.exists()
    with open(test_file_path, "r") as tfp:
        contents = tfp.read()
        assert contents
        assert contents.find("logger") != -1
    # Cleanup
    branch_name = sc.get_active_branch_name(coder.repo)
    sc.use_branch(coder.repo, "main")
    sc.delete_branch(coder.repo, branch_name)
