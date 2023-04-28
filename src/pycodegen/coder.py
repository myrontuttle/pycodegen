from typing import Dict, Optional

import json
import logging
import os
import re
import subprocess
from json import JSONDecodeError
from pathlib import Path

import click
import tomli
from pathvalidate import sanitize_filename

from pycodegen import llm, sc, tester, todo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


logger = logging.getLogger(__name__)

TEMP_FILE = "temp.py"
LOGGER_CODE = (
    "\nimport logging\n\n"
    "logging.basicConfig(\n"
    "    level=logging.INFO,\n"
    "    format='%(asctime)s [%(levelname)s] %(message)s',\n"
    "    datefmt='%Y-%m-%d %H:%M:%S'\n)\n\n"
    "logger = logging.getLogger(__name__)\n\n"
)


def bump_version(issue_type: str) -> None:
    """
    Bumps the version in pyproject.toml based on issue type
    Args:
        issue_type: The type of issue that was worked on

    Returns:
        None
    """
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        logger.warning(f"No pyproject.toml found at {pyproject_path}")
        return

    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)

    version = pyproject["project"]["version"]
    logger.info(f"Current version: {version}")

    if issue_type == "feature":
        cp_format = subprocess.run(
            [
                "pdm",
                "bump",
                "minor",
            ],
            capture_output=True,
        )
    else:
        cp_format = subprocess.run(
            [
                "pdm",
                "bump",
                "micro",
            ],
            capture_output=True,
        )
    if cp_format.returncode == 0:
        logger.info(cp_format.stdout)
    else:
        logger.error(cp_format.stderr)


def just_the_code(llm_text: str) -> Optional[str]:
    """
    Returns just the code portion of an LLM response.
    Args:
        llm_text

    Returns:
        Just the code portion of the text provided
    """
    if "```python" in llm_text:
        start_idx = llm_text.find("```python") + 10
        end_idx = llm_text.find("```", start_idx)
        return llm_text[start_idx:end_idx]
    elif "```" in llm_text:
        start_idx = llm_text.find("```") + 4
        end_idx = llm_text.find("```", start_idx)
        return llm_text[start_idx:end_idx]

    if "import " not in llm_text and "def " not in llm_text:
        # Probably not python code
        logger.warning("LLM response doesn't appear to be code: ")
        logger.warning(llm_text)
        return '"""' + llm_text + '"""'
    else:
        # We'll probably need to add more conditions as we encounter them
        return llm_text


def add_text_to_module(module_text: str, text_to_add: str) -> str:
    """
    Adds function text to module text in an organized way
    Args:
        module_text
        text_to_add

    Returns:
        Updated module text
    """
    class_loc = module_text.find("class ")
    main_loc = module_text.find('if __name__ == "__main__":')
    if class_loc != -1:
        end_of_class = module_text.find("\n\n\n", class_loc)
        if end_of_class == -1:
            # Nothing after last class function
            module_text += "\n\n" + text_to_add + "\n"
        else:
            # Adding text to end of class
            module_text = (
                f"{module_text[:end_of_class + 2]}"
                f"{text_to_add}"
                f"{module_text[end_of_class + 2:]}"
            )
    elif main_loc != -1:
        # No class, but main function needs to stay at end
        module_text = (
            f"{module_text[:main_loc]}"
            f"{text_to_add}\n\n\n"
            f"{module_text[main_loc:]}"
        )
    else:
        # No class or main function, just add to end
        module_text += "\n\n" + text_to_add + "\n"
    return module_text


def add_logging(script_content: str) -> str:
    """Adds code for a logger to a python script"""
    if script_content.find("import logging") != -1:
        logger.info("Logging already included")
        return script_content
    import_re = re.compile(r"^\s*import\s.*$", re.MULTILINE)
    from_import_re = re.compile(r"^\s*from\s.*$", re.MULTILINE)
    last_import_match = None
    for match in reversed(list(import_re.finditer(script_content))):
        if (
            last_import_match is None
            or match.start() > last_import_match.start()
        ):
            last_import_match = match
    for match in reversed(list(from_import_re.finditer(script_content))):
        if (
            last_import_match is None
            or match.start() > last_import_match.start()
        ):
            last_import_match = match
    if last_import_match is not None:
        last_import_line = last_import_match.end()
        return (
            script_content[:last_import_line]
            + LOGGER_CODE
            + script_content[last_import_line:]
        )
    else:
        return LOGGER_CODE + script_content


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def code():
    pass


@code.command()
@click.argument("repo_owner")
@click.argument("repo_name")
@click.option("-i", "--issue_num", type=int)
def start(repo_owner: str, repo_name: str, issue_num: Optional[int]) -> None:
    coder = Coder(repo_owner, repo_name)
    response = coder.open_issue(issue_num)
    if response == 0:
        click.echo("Successfully started issue")


@code.command()
@click.argument("repo_owner")
@click.argument("repo_name")
@click.option(
    "-m",
    "--commit_msg",
    default="",
    help="Commit message. " "Generated automatically" " if not provided",
)
def finish(repo_owner: str, repo_name: str, commit_msg="") -> None:
    coder = Coder(repo_owner, repo_name)
    response = coder.finish_issue(commit_msg)
    if response == 0:
        click.echo("Successfully completed issue")


class Coder:
    """
    Coder Class
    """

    work_dir = Path("C:\\Users\\myron\\PycharmProjects")
    host = "https://github.com"

    def __init__(self, owner_name: str, repo_name: str):
        """
        Initializes a coder on a project repo
        Args:
            owner_name
            repo_name
        """
        self.repo_owner = owner_name
        self.repo_name = repo_name
        self.repo = sc.use_repo(self.work_dir, self.repo_name, self.repo_owner)
        self.repo_path = self.work_dir.joinpath(self.repo_name)
        tester.create_test_dirs(self.repo_path)

        venv_path = self.repo_path.joinpath(".venv")
        # TODO: Use appropriate python version in following subprocesses
        if not venv_path.exists():
            os.chdir(self.repo_path)
            cp_setup = subprocess.run(
                [
                    "pdm",
                    "venv",
                    "create",
                    "3.9",
                    "-v",
                ],
                capture_output=True,
            )
            cp_setup2 = subprocess.run(
                [
                    "pdm",
                    "venv",
                    "activate",
                    "in-project",
                ],
                capture_output=True,
                shell=True,
            )  # nosec B602
            subprocess.run(
                [
                    "pdm",
                    "use",
                    "3.9",
                    "-i",
                    "-f",
                    "-vv",
                ],
                capture_output=True,
            )
            subprocess.run(
                [
                    "make",
                    "install",
                ],
                capture_output=True,
            )
            if cp_setup2.returncode == 0:
                # May be too much to push to logs
                logger.info(cp_setup.stdout)
            else:
                logger.error(cp_setup.stderr)

    def open_issue(self, issue_num: Optional[int]) -> int:
        """
        Open an issue to work on. Either a specific issue or next available
        Args:
            issue_num

        Returns:
            response code
        """
        github_repo = todo.get_repo(self.repo_owner, self.repo_name)
        if issue_num:
            issue = todo.get_issue(github_repo, issue_num)
        else:
            issue = todo.get_next_issue(self.repo_owner, self.repo_name)
        if not issue:
            return 1
        logger.info(f"Working on issue {issue.number}: {issue.title}")

        # Pull repo
        if self.repo.active_branch.name == "main":
            self.repo.git.pull()
        else:
            self.repo.git.fetch()
        logger.info("Pulled repo")

        # Checkout git branch
        branch_name = todo.issue_title_to_branch_name(github_repo, issue)
        sc.use_branch(self.repo, branch_name)
        logger.info(f"Created branch {branch_name}")

        # TODO: Account for multiple packages, no package, or package name
        #  different from repo name
        package_name = self.repo_name.replace("-", "_")

        # Recommend module to work with
        src_file_name = self.recommend_filename(issue_num, package_name)
        logger.info(f"Recommended source file {src_file_name}")

        # Create unit tests if bug or feature
        issue_type = todo.get_issue_type(github_repo, issue)
        if issue_type == "bug" or issue_type == "feature":
            unit_tests = tester.create_unit_tests(
                src_file_name,
                issue.body,
                issue_type,
                package_name,
            )
            test_path = tester.write_unit_tests_to_file(
                self.repo_path,
                src_file_name,
                unit_tests,
            )
            logger.info(f"Created test file {test_path}")
        else:
            unit_tests = ""
            logger.info(f"No unit tests created for issue_type={issue_type}")

        # Create functional test if new feature
        if issue_type == "feature":
            feature_path = tester.create_feature(self.repo_path, issue)
            logger.info(f"Created feature file {feature_path}")
            test_path = tester.create_step_defs(feature_path)
            if test_path:
                logger.info(f"Created functional test file {test_path}")

        # Recommended library
        libs = self.recommend_libraries(issue_num)
        best_lib = ""
        if libs:
            best_lib = list(libs)[0]

        # Start writing code for the issue
        self.write_src_code(issue_num, src_file_name, unit_tests, best_lib)

        return 0

    def finish_issue(self, commit_msg: str) -> int:
        """
        Formats, commits, merge, and push any work on active branch
        Args:
            commit_msg: Commit message
        Returns:
            Completion response code
        """
        # Make sure were in repo root dir
        os.chdir(self.repo_path)

        # Auto increment version based on branch name
        branch_name = sc.get_active_branch_name(self.repo)
        issue_type = todo.issue_type_from_branch_name(branch_name)
        bump_version(issue_type)

        # Format code
        cp_format = subprocess.run(
            [
                "make",
                "format",
            ],
            capture_output=True,
        )
        if cp_format.returncode == 0:
            logger.info(cp_format.stdout)
        else:
            logger.error(cp_format.stderr)
            return 1
        sc.add_files(self.repo, ["."])

        # Make commit msg based on branch_name and work done
        branch_name = sc.get_active_branch_name(self.repo)
        if not commit_msg:
            commit_msg = sc.generate_commit_msg(self.repo, branch_name)
        else:
            issue_type = todo.issue_type_from_branch_name(branch_name)
            issue_number = todo.issue_num_from_branch_name(branch_name)
            commit_msg = sc.add_commit_message_info(
                commit_msg,
                issue_type,
                issue_number,
            )
        logger.info(f"Commit message: {commit_msg}")

        git_response_code = sc.commit(self.repo, commit_msg)
        if git_response_code != 0:
            return 1
        logger.info("Committed changes")
        git_response_code = sc.safe_merge(self.repo, branch_name)
        if git_response_code != 0:
            return 1
        logger.info("Merged changes")
        git_response_code = sc.push_to_origin(self.repo)
        if git_response_code != 0:
            return 1
        logger.info("Pushed changes")
        sc.delete_branch(self.repo, branch_name)
        logger.info(f"Deleted branch {branch_name}")
        return 0

    def recommend_libraries(self, issue_num: int) -> Optional[Dict[str, str]]:
        """
        Recommends a library based on an issue
        Args:
            issue_num

        Returns:
            Recommended library
        """
        # Get Issue
        github_repo = todo.get_repo(self.repo_owner, self.repo_name)
        issue = todo.get_issue(github_repo, issue_num)
        # TODO: Consider adding project description for context in prompt
        # Ask Chat LLM what libraries it would recommend for issue
        prompt = (
            f"In the form of a JSON object, "
            f"what are the top python libraries I could use for the following "
            f"issue?\n{issue.title}\n{issue.body}\nRespond in the "
            f"form of a JSON object with each library name as "
            f"the key and a string of two sentences describing the "
            f"library and why to use it for this issue as the value."
        )
        response: str = llm.complete_prompt(prompt)
        if not response:
            return None

        click.echo(f"Recommended Libraries for issue #{str(issue_num)}:")
        click.echo(response)
        response = response[response.find("{") : response.find("}") + 1]
        if response.find("': ") != -1:
            response = response.replace("'", '"')
        try:
            recommendations = json.loads(response)
        except JSONDecodeError as jde:
            logger.warning("Can't load LLM response as JSON. " + str(jde))
            logger.warning("Response: " + response)
            return None

        # Lookup alternatives
        rec_list = " or ".join(recommendations.keys())
        # TODO: Do this with a web search to get current best practices
        alt_prompt = (
            f"In the form of a python dictionary, what are some "
            f"alternative python libraries to using {rec_list}? "
            f"Respond in the form of a python dictionary with each "
            f"library name as the key and a string of two "
            f"sentences describing the library and why to use it "
            f"for this ticket as the value."
        )
        alt_response: str = llm.complete_prompt(alt_prompt)
        if alt_response:
            alt_response = alt_response.replace("'", '"')
            alt_response = alt_response[
                alt_response.find("{") : alt_response.find("}") + 1
            ]
            try:
                recommendations.update(json.loads(alt_response))
            except JSONDecodeError as jde:
                logger.error(str(jde))
                logger.debug(
                    "Unable to get library alternatives.\n"
                    f"Messages: {str(alt_prompt)}\n"
                    f"Response: {alt_response}"
                )

        # If the project is already using the libraries, recommend those
        to_recommend = {}
        with open(self.repo_path.joinpath("pyproject.toml"), mode="rb") as fp:
            project_config = tomli.load(fp)
        dependencies = project_config["project"]["dependencies"]
        for rec in recommendations.keys():
            if rec in dependencies:
                to_recommend[rec] = recommendations[rec]
        if to_recommend:
            return to_recommend
        else:
            return recommendations

    def add_library(self, lib_name: str) -> None:
        """
        Adds a library to the project dependencies using PDM if it's not
        already a dependency
        """
        os.chdir(self.repo_path)
        with open(self.repo_path.joinpath("pyproject.toml"), mode="rb") as fp:
            project_config = tomli.load(fp)
        dependencies = project_config["project"]["dependencies"]
        if lib_name in dependencies:
            logger.info(f"Library: {lib_name} already in project dependencies")
            return None
        cp_add_lib = subprocess.run(
            [
                "pdm",
                "add",
                f"{lib_name}",
            ],
            capture_output=True,
        )
        if cp_add_lib.returncode == 0:
            logger.info(cp_add_lib.stdout)
        else:
            logger.error(cp_add_lib.stderr)

    def recommend_filename(self, issue_num: int, pkg_name="") -> str:
        """
        Recommend a filename to create or add to for the issue
        Args:
            issue_num: Issue number
            pkg_name: Package name

        Returns:
            Filename
        """
        # Get Issue
        github_repo = todo.get_repo(self.repo_owner, self.repo_name)
        issue = todo.get_issue(github_repo, issue_num)
        # Get existing src files
        if not pkg_name:
            # Assume package name same as repo name
            pkg_name = self.repo_name.replace("-", "_")
        src_dir = self.repo_path.joinpath("src").joinpath(pkg_name)
        src_files = [
            str(f)
            for f in os.listdir(src_dir)
            if os.path.isfile(os.path.join(src_dir, f))
            and str(f).endswith(".py")
            and str(f) != "__init__.py"
        ]
        # Ask Chat LLM what filename it would recommend for issue
        if src_files:
            prompt = (
                f"Recommend one of these source files ("
                f"{', '.join(src_files)}) to add "
                f"python code that would solve the below issue. "
                f"If none of the source files is appropriate, respond with "
                f"a new file name.\n"
                f"Issue: {issue.title}\n{issue.body}\n"
                f"Respond with just the name of the file."
            )
        else:
            prompt = (
                f"What should I name the python script that solves the "
                f"following issue?\n"
                f"Issue: {issue.title}\n{issue.body}\n"
                f"Respond with just the name of the file."
            )

        response: str = llm.complete_prompt(prompt)
        if response:
            if response.find(" ") != -1:
                response = response[response.rfind(" ") + 1 :]
            response = sanitize_filename(response)
            if not response.endswith(".py"):
                response += ".py"
            return response
        else:
            logger.error(
                f"No file name recommended for issue #: {issue_num}."
                f"Using {TEMP_FILE}."
            )
            return TEMP_FILE

    def write_src_code(
        self, issue_num: int, src_file_name: str, unit_tests="", lib_name=""
    ) -> None:
        """
        Writes code to the file provided (creating if it doesn't exist)
        Args:
            issue_num
            src_file_name
            unit_tests
            lib_name

        Returns:
            None
        """
        # Get Issue
        github_repo = todo.get_repo(self.repo_owner, self.repo_name)
        issue = todo.get_issue(github_repo, issue_num)

        # Get existing file header
        src_file_path = (
            self.repo_path.joinpath("src")
            .joinpath(self.repo_name.replace("-", "_"))
            .joinpath(src_file_name)
        )
        src_file_contents = ""
        if src_file_path.exists():
            with open(src_file_path, "r") as fp:
                src_file_contents = fp.read()
        file_header = ""
        if src_file_contents:
            file_header = (
                "The existing source file starts with:\n"
                + src_file_contents[: src_file_contents.find("def")]
            )

        # Get unit tests that the code should pass
        unit_test_prompt = ""
        if unit_tests:
            unit_test_prompt = (
                f"The code produced should pass the "
                f"following unit tests.\n{unit_tests}\n"
            )

        # Get Library to use
        use_lib = ""
        if lib_name:
            use_lib = f"Use {lib_name} in the solution."

        # TODO: Consider adding project description for context in prompt
        # Ask Chat LLM to provide code for issue
        prompt = (
            f"Provide python code for a solution to the following "
            f"issue.\n"
            f"Issue: {issue.title}\n{issue.body}\n\n"
            f"{use_lib}\n\n"
            f"{unit_test_prompt}\n"
            f"Respond with just the python code.\n"
            f"{file_header}"
        )
        response: str = llm.complete_prompt(prompt)
        if response:
            if src_file_contents:
                # Remove existing source file header from response
                response = response.replace(file_header, "")
                src_file_contents = add_text_to_module(
                    src_file_contents,
                    just_the_code(response),
                )
            else:
                src_file_contents = just_the_code(response)
                src_file_contents = add_logging(src_file_contents)
            with open(src_file_path, "w") as fp:
                fp.write(src_file_contents.replace("\r", ""))
            logger.info(f"Added the following to file {src_file_path}")
            logger.info(f"{src_file_contents}")
        else:
            logger.warning(f"No response from LLM for messages: {prompt}")
            logger.warning("No source code written.")


if __name__ == "__main__":
    code()
