Feature: Library Recommender
  As a dev lead
  I want a recommendation of which library I should use for a coding task
  So that I can add it to my project

  Scenario: Recommend Library
    Given my current project
    When I provide a description of a coding task
    Then I get a recommendation for a library to use
