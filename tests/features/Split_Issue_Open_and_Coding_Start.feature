Feature: Split Issue Open and Coding Start
  As a dev lead
  I want the coder to have separate commands for opening an issue and starting coding
  So that I can get different coding assistance based on the issue

  Scenario: Just Open Issue
    Given a quick fix
    When I ask the coder to open the issue
    Then it just creates the branch

  Scenario: Start Coding
    Given a new feature
    When I ask the coder to start coding
    Then it creates tests and source code
