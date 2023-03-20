Feature: Functional Test Creation
  As a development lead,
  I want a functional test created for each feature request,
  so that I can verify that developed code meets the requirements of the feature request.

Scenario: Creating a functional test for a new feature request
  Given an open issue in the GitHub repo with the "enhancement" label
  When coding starts for the new issue
  Then a functional test is created to test the feature described in the issue
