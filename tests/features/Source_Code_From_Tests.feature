Feature: Source Code From Tests
  As a dev lead
  I want the coder to use functions that have been defined in unit tests as a basis for source files
  So that the source files match up with the test files that are testing them

  Scenario: Source Code From Tests
    Given a repo
    When I pass a set of unit tests
    Then source code that passes those tests will be generated
    And the unit test file will import the source code
