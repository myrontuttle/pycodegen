Feature: Automatically Increment Version Based On Change
  As a dev lead
  I want the coder to automatically increment the project version based on code changes
  So that the version accurately reflects semantic versioning

  Scenario: Automatically Increment Version
    Given a code change for an issue
    When the coder finishes work on that issue
    Then the project version is updated based on the work
