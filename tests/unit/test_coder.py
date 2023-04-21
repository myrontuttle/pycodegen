from pycodegen import coder


def test_just_the_code_non_code_response():
    response = "I'm sorry, but I cannot provide code for that action."
    jtc = coder.just_the_code(response)
    assert not jtc


def test_just_the_code_with_expl():
    response = """Here's a possible solution in Python using Flask framework:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    # Replace the following code with your program's output
    output = "<h1>Hello, World!</h1>"
    return output

if __name__ == '__main__':
    app.run()
```

When you run this code, a local web server will be started and you can access the program's output by opening your browser to the URL http://localhost:5000/.

Note: this is a simple example and you may need to modify the code to fit your specific use case."""  # noqa: E501
    jtc = coder.just_the_code(response)
    assert jtc.startswith("from flask import Flask")


def test_just_the_code_already_code():
    response = """import logging

# Set up the logger
logger = logging.getLogger(__name__)

# Add a file handler to the logger
handler = logging.FileHandler('example.log')
handler.setLevel(logging.INFO)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Example usage of logging
def example_function():
    logger.info('This is an info message.')
    logger.warning('This is a warning message.')
    logger.error('This is an error message.')
    logger.critical('This is a critical message.')"""
    jtc = coder.just_the_code(response)
    assert jtc == response


def test_just_the_code_with_wrap():
    response = """```
from github import Github

# Instantiate PyGithub's Github object using an access token or username and password
g = Github(access_token)

# Get the repository where the issue is located
repo = g.get_repo("username/repository_name")

# Create a new issue
new_issue = repo.create_issue(title="Test Issue", body="This is a test issue for PyGithub")

# Retrieve the test code and format it
test_code = f"def test_{new_issue.number}():\n    # Insert test code here\n    assert True"

# Create a new python file and write the test code to it
with open(f"test_{new_issue.number}.py", "w") as f:
    f.write(test_code)
```"""  # noqa: E501
    jtc = coder.just_the_code(response)
    assert "```" not in jtc


def test_add_logging_no_imports():
    script_content = "print('Hello, world!')"
    mod_content = coder.add_logging(script_content)
    assert (
        mod_content == "\nimport logging\n\n"
        "logging.basicConfig(\n"
        "\tlevel=logging.INFO,\n"
        "\tformat='%(asctime)s [%(levelname)s] %(message)s',\n"
        "\tdatefmt='%Y-%m-%d %H:%M:%S'\n)\n\n"
        "logger = logging.getLogger(__name__)\n\n"
        "print('Hello, world!')"
    )


def test_add_logging_one_import():
    script_content = "import os\nprint('Hello, world!')"
    mod_content = coder.add_logging(script_content)
    assert (
        mod_content == "import os\nimport logging\n\n"
        "logging.basicConfig(\n"
        "\tlevel=logging.INFO,\n"
        "\tformat='%(asctime)s [%(levelname)s] %(message)s',\n"
        "\tdatefmt='%Y-%m-%d %H:%M:%S'\n)\n\n"
        "logger = logging.getLogger(__name__)\n\n\nprint("
        "'Hello, world!')"
    )


def test_add_logging_multiple_imports():
    script_content = "import os\nimport sys\nprint('Hello, world!')"
    mod_content = coder.add_logging(script_content)
    assert (
        mod_content == "import os\nimport sys\nimport logging\n\n"
        "logging.basicConfig(\n"
        "\tlevel=logging.INFO,\n"
        "\tformat='%(asctime)s [%(levelname)s] %(message)s',\n"
        "\tdatefmt='%Y-%m-%d %H:%M:%S'\n)\n\n"
        "logger = logging.getLogger(__name__)\n\n\nprint("
        "'Hello, world!')"
    )


def test_add_logging_from_import():
    script_content = "from os import path\nprint('Hello, world!')"
    mod_content = coder.add_logging(script_content)
    assert (
        mod_content == "from os import path\nimport logging\n\n"
        "logging.basicConfig(\n"
        "\tlevel=logging.INFO,\n"
        "\tformat='%(asctime)s [%(levelname)s] %(message)s',\n"
        "\tdatefmt='%Y-%m-%d %H:%M:%S'\n)\n\n"
        "logger = logging.getLogger(__name__)\n\n\nprint("
        "'Hello, world!')"
    )


def test_add_logging_no_match():
    script_content = (
        "print('Hello, world!')\n\n# This is a "
        "comment\n\nprint('Goodbye, world!')"
    )
    mod_content = coder.add_logging(script_content)
    assert (
        mod_content == "\nimport logging\n\n"
        "logging.basicConfig(\n"
        "\tlevel=logging.INFO,\n"
        "\tformat='%(asctime)s [%(levelname)s] %(message)s',\n"
        "\tdatefmt='%Y-%m-%d %H:%M:%S'\n)\n\n"
        "logger = logging.getLogger(__name__)\n\n"
        "print('Hello, world!')\n\n# This is "
        "a comment\n\nprint('Goodbye, world!')"
    )


def test_logging_already_added():
    script_content = (
        "import logging\n\n"
        "logging.basicConfig(\n"
        "\tlevel=logging.INFO,\n"
        "\tformat='%(asctime)s [%(levelname)s] %(message)s',\n"
        "\tdatefmt='%Y-%m-%d %H:%M:%S'\n)\n\n"
        "logger = logging.getLogger(__name__)\n\n\n"
        "print('Hello, world!')"
    )
    mod_content = coder.add_logging(script_content)
    assert mod_content == script_content
