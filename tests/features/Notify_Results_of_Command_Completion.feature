Feature: Notify Results of Command Completion
  As a dev lead
  I want the coder to notify the results of commands using Click
  So I can see what happened after calling the command

  Scenario: Notify on Start and Stop
    Given a coding project
    When I issue the 'start' or 'stop' commands on the command line using the Click library
    Then there is a message indicating the result of the command upon completion
