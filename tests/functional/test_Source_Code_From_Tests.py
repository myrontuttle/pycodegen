"""Source Code From Tests feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen.coder import Coder

owner = "myrontuttle"
test_repo = "test_project"
test_issue = 5


@scenario(
    "../features/Source_Code_From_Tests.feature", "Source Code From Tests"
)
def test_source_code_from_tests():
    """Source Code From Tests."""


@given("a repo")
def a_repo():
    """a repo."""


@when("I pass a set of unit tests")
def pass_unit_tests():
    """I pass a set of unit tests."""


@then("source code that passes those tests will be generated")
def generate_source_code():
    """source code that passes those tests will be generated."""
    coder = Coder(owner, test_repo)
    coder.open_issue(test_issue)


@then("the unit test file will import the source code")
def test_import_source_code():
    """the unit test file will import the source code."""
