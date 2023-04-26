Feature: Use Existing Source Files
  As a dev lead
  I want the coder to use existing source code files in the project when starting new issues
  So that they take advantage of existing libraries and written code

  Scenario: Use Existing Source Files
    Given a project repo
    When I start a new issue
    Then existing source code files are considered for development
