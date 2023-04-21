Feature: Write Commit Message Automatically
  As a developer
  I want commit messages written automatically
  So that I don't have to think about what to write

  \# Per https://github.com/Nutlope/aicommits
  \# Run git diff to grab all the latest code changes,
  \# send them to OpenAI's GPT-3,
  \# then return the AI generated commit message.

  Scenario: Automatic Commit Message
    Given a code change on a branch
    When that branch is added and committed
    Then a commit message is automatically created
