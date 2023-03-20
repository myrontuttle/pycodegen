Feature: Cleanup Branch When Done
  As a dev lead
  I want the branch the coder was working on deleted upon completion
  So that there are not multiple branches left open

  Scenario: Delete branch
    Given a branch other than main
    When work is completed for the issue that branch was opened for
    Then the branch is deleted
