"""Functional Test Creation feature tests."""
from pathlib import Path

from pytest_bdd import given, scenario, then, when

from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue_num = 3


@scenario(
    "..\\features\\Create_Functional_Test.feature",
    "Creating a functional test for a new feature request",
)
def test_creating_a_functional_test_for_a_new_feature_request():
    """Creating a functional test for a new feature request."""


@given('an open issue in the GitHub repo with the "enhancement" label')
def get_enhancement_issue():
    """an open issue in the GitHub repo with the "enhancement" label."""
    return test_issue_num


@when("coding starts for the new issue")
def start_coding():
    """coding starts for the new issue."""
    coder = Coder(repo_owner, test_repo)
    coder.open_issue(test_issue_num)


@then(
    "a functional test is created to test the feature described in the issue"
)
def func_test_exists():
    """
    a functional test is created to test the feature described in the issue.
    """
    func_test_path = Path(
        "C:\\Users\\myron\\PycharmProjects\\test_project"
        "\\tests\\functional\\test_Test_an_issue.py"
    )
    assert func_test_path.exists()
