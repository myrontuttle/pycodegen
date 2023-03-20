from pycodegen import todo


def test_issue_title_to_branch_name():
    # TODO: Mock an Issue and pass it to todo.issue_title_to_branch_name
    pass


def test_issue_num_from_branch_name():
    branch_name = "feat/3/test_Test_an_issue"
    issue_num = todo.issue_num_from_branch_name(branch_name)
    assert issue_num == 3
