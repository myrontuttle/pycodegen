Feature: Close Associated Issue When Committing
  As a dev lead
  I want commit messages to automatically add "Fixes #xx" where 'xx' is the issue number to commits when completing code changes
  so that associated issue is closed.

  Scenario: Close Associated Issue
    Given the coder is working on an open branch
    When they complete the active issue
    Then the commit message automatically includes "Fixes " and the number of the issue
