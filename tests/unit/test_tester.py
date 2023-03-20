from pycodegen import tester

test_issue_body = """As a development lead,
I want a functional test created for each feature request,
so that I can verify that developed code meets the requirements.

Scenario: Functional Test Creation
Given a new issue in the GitHub repo with the "enhancement" label
When coding starts for the new issue
Then a functional test is created to test the feature."""


def test_get_scenarios_from_issue_body():
    scenarios = tester.get_scenarios_from_issue_body(test_issue_body)
    assert (
        scenarios[0]
        == """Scenario: Functional Test Creation
Given a new issue in the GitHub repo with the "enhancement" label
When coding starts for the new issue
Then a functional test is created to test the feature."""
    )


def test_indent_sub_lines():
    indented_body = """  As a development lead,
  I want a functional test created for each feature request,
  so that I can verify that developed code meets the requirements.

  Scenario: Functional Test Creation
    Given a new issue in the GitHub repo with the "enhancement" label
    When coding starts for the new issue
    Then a functional test is created to test the feature.
"""
    assert tester.indent_sub_lines(test_issue_body) == indented_body
