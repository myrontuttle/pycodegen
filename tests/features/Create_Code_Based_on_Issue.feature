Feature: Create Code Based on Issue
  As a dev lead
  I want a procedure for generating code
  So that I can complete a ticket

  Scenario: Create Code from Issue
    Given an open issue for a repo
    When I provide the text of the issue and a file to add code to
    Then the program generates code based on that issue.
