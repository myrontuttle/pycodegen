"""Generate Test Cases For Issue feature tests."""
from pathlib import Path

from pytest_bdd import given, scenario, then, when

from pycodegen import tester, todo

repo_owner = "myrontuttle"
test_repo = "test_project"
repo_path = Path("C:\\Users\\myron\\PycharmProjects\\test_project")
test_issue_num = 5


@scenario(
    "../features/Generate_Test_Cases_For_Issue.feature", "Generate Test Cases"
)
def test_generate_test_cases():
    """Generate Test Cases."""


@given("an issue in Github")
def an_issue_in_github():
    """an issue in Github."""


@when("the issue is read")
def the_issue_is_read():
    """the issue is read."""


@then("test cases are generated for the issue to be tested")
def generate_test_cases():
    """test cases are generated for the issue to be tested."""
    github_repo = todo.get_repo(repo_owner, test_repo)
    issue = github_repo.get_issue(test_issue_num)
    issue_body = issue.body
    issue_type = todo.get_issue_type(github_repo, issue)
    src_file_name = "webpage.py"
    package_name = "test_project"
    test_path = tester.create_unit_tests(
        src_file_name,
        issue_body,
        issue_type,
        package_name,
    )
    assert Path(test_path).exists()
