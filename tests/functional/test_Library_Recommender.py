"""Library Recommender feature tests."""

from pytest_bdd import given, scenario, then, when

from pycodegen.coder import Coder

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue = 5  # Create a Webpage


@scenario("../features/Library_Recommender.feature", "Recommend Library")
def test_recommend_library():
    """Recommend Library."""


@given("my current project")
def open_my_current_project():
    """my current project."""


@when("I provide a description of a coding task")
def provide_description():
    """I provide a description of a coding task."""


@then("I get a recommendation for a library to use")
def check_for_recommendation():
    """I get a recommendation for a library to use."""
    coder = Coder(repo_owner, test_repo)
    rec_libs = coder.recommend_libraries(test_issue)
    assert rec_libs
