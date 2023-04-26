Feature: Generate Test Cases For Issue
  As a dev lead
  I want the coder to generate useful test cases for an issue
  So that code that is generated for the issue can be tested

  Scenario: Generate Test Cases
    Given an issue in Github
    When the issue is read
    Then test cases are generated for the issue to be tested
