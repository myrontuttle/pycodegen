from pycodegen import todo


def test_issue_title_to_branch_name():
    # TODO: Mock an Issue and pass it to todo.issue_title_to_branch_name
    pass


def test_issue_num_from_branch_name():
    branch_name = "feat/3/test_Test_an_issue"
    issue_num = todo.issue_num_from_branch_name(branch_name)
    assert issue_num == "3"


def test_get_issue_comments():
    repo = todo.get_repo("myrontuttle", "test_project")
    issue = todo.get_issue(repo, 3)
    comments = todo.get_issue_comments(issue)
    assert comments
    assert comments[0] == "Re-opening for further testing"


def test_write_issue_comment():
    repo = todo.get_repo("myrontuttle", "test_project")
    issue = todo.get_issue(repo, 3)
    comment = "This is a test comment"
    todo.write_issue_comment(issue, comment)
    comments = todo.get_issue_comments(issue)
    assert comments
    assert comments[-1] == comment
    todo.delete_last_issue_comment(issue)
