"""Use Existing Source Files feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue_num = 5


@scenario(
    "../features/Use_Existing_Source_Files.feature",
    "Use Existing Source Files",
)
def test_use_existing_source_files():
    """Use Existing Source Files."""


@given("a project repo")
def project_repo():
    """a project repo."""


@when("I start a new issue")
def start_new_issue():
    """I start a new issue."""


@then("existing source code files are considered for development")
def consider_existing_code():
    """existing source code files are considered for development."""
    coder = Coder(repo_owner, test_repo)
    file_name = coder.recommend_filename(test_issue_num)
    assert file_name.endswith(".py")
    file_path = coder.repo_path.joinpath("src", coder.repo_name, file_name)
    with open(file_path, "w") as f:
        f.write("print('Imagine this code generates a webpage.')")
    next_rec = coder.recommend_filename(test_issue_num)
    assert next_rec == file_name
