Feature: Read and Write Comments for Issue
  As a dev lead
  I want the coder to read and write comments for a GitHub issue
  So that they can ask questions and get answers for how to develop an issue

  Scenario: Read Comments for Issue
    Given an open issue in GitHub
    When the coder opens the issue
    Then they read all comments for that issue
    And they comment with any questions they have about the issue
