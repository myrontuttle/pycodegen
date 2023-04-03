from typing import Dict, Optional

import json
import logging
import os
import subprocess
from json import JSONDecodeError
from pathlib import Path

import click
import tomli
from github.Issue import Issue
from pathvalidate import sanitize_filename

from pycodegen import llm, sc, tester, todo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

TEMP_FILE = "temp.py"


def best_library(libs: Dict[str, str]) -> str:
    """
    Evaluates a set of python libraries and returns the best
    Returns
    -------
    The top library from the set
    """
    return list(libs)[0]
    # For each library
    # Find the page for it on PyPI
    # Ensure it supports the Python version of the project.
    # Check the Development Status (want Production/Stable)
    # Check for project link to the project’s source code
    # Find the package on libraries.io
    # Check on dependent packages
    # Check the SourceRank
    # Find the source code in GitHub
    # Check on the social proof (Watchers, Stars, Forks, PR's, Issues)
    # Check the package's license


def just_the_code(llm_text: str) -> str:
    """
    Returns just the code portion of an LLM response.
    Parameters
    ----------
    llm_text

    Returns
    -------
    Just the code portion of the text provided
    """
    if llm_text.startswith("```python"):
        return llm_text[9 : llm_text.find("```")]
    elif llm_text.startswith("```"):
        return llm_text[3 : llm_text.find("```")]
    else:
        # We'll probably need to add more conditions as we encounter them
        return llm_text


def add_text_to_module(module_text: str, text_to_add: str) -> str:
    """
    Adds function text to module text in an organized way
    Parameters
    ----------
    module_text
    text_to_add

    Returns
    -------
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
    coder.open_issue(issue_num)


@code.command()
@click.argument("repo_owner")
@click.argument("repo_name")
@click.argument("commit_msg")
def stop(repo_owner: str, repo_name: str, commit_msg: str) -> None:
    coder = Coder(repo_owner, repo_name)
    coder.complete_active_issue(commit_msg)


class Coder:
    """
    Coder Class
    """

    work_dir = Path("C:\\Users\\myron\\PycharmProjects")
    host = "https://github.com"

    def __init__(self, owner_name: str, repo_name: str):
        """
        Initializes a coder on a project repo
        Parameters
        ----------
        owner_name
        repo_name
        """
        self.repo_owner = owner_name
        self.repo_name = repo_name
        self.repo = sc.use_repo(self.work_dir, self.repo_name, self.repo_owner)
        self.repo_path = self.work_dir.joinpath(self.repo_name)
        tester.create_bdd_dirs(self.repo_path)

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

    def open_issue(self, issue_num: Optional[int]) -> Optional[Issue]:
        """
        Open an issue to work on. Either a specific issue or next available
        Parameters
        ----------
        issue_num

        Returns
        -------
        The issue we're working on if available
        """
        if issue_num:
            issue = todo.get_issue(self.repo_owner, self.repo_name, issue_num)
        else:
            issue = todo.get_next_issue(self.repo_owner, self.repo_name)
        if not issue:
            return None

        # Pull repo
        if self.repo.active_branch.name == "main":
            self.repo.git.pull()
        else:
            self.repo.git.fetch()

        # Checkout git branch
        branch_name = todo.issue_title_to_branch_name(
            self.repo_owner, self.repo_name, issue
        )
        sc.use_branch(self.repo, branch_name)

        # Create functional test
        if branch_name.startswith(todo.feature_prepend):
            feature_path = tester.create_feature(self.repo_path, issue)
            tester.create_step_defs(feature_path)

        # Add recommended library
        libs = self.recommend_libraries(issue_num)
        best_lib = ""
        if libs:
            best_lib = best_library(libs)
            self.add_library(best_lib)

        # Start writing code for the issue
        file_name = self.recommend_filename(issue_num)
        self.write_code(issue_num, file_name, best_lib)

        return issue

    def complete_active_issue(self, commit_msg: str):
        """
        Formats, commits, merge, and push any work on active branch
        """
        os.chdir(self.repo_path)
        cp_format = subprocess.run(
            [
                "make",
                "format",
            ],
            capture_output=True,
        )
        if cp_format.returncode == 0:
            # May be too much to push to logs
            logger.info(cp_format.stdout)
        else:
            logger.error(cp_format.stderr)
            return
        branch_name = sc.get_active_branch_name(self.repo)
        # TODO: Make commit msg based on branch_name and work done
        issue_num = todo.issue_num_from_branch_name(branch_name)
        if issue_num:
            commit_msg = "Fixes #" + str(issue_num) + ". " + commit_msg
        git_response_code = sc.add_and_commit(self.repo, ["."], commit_msg)
        if git_response_code != 0:
            return
        git_response_code = sc.safe_merge(self.repo, branch_name)
        if git_response_code != 0:
            return
        git_response_code = sc.push_to_origin(self.repo)
        if git_response_code != 0:
            return
        sc.delete_branch(self.repo, branch_name)

    def recommend_libraries(self, issue_num: int) -> Optional[Dict[str, str]]:
        """
        Recommends a library based on an issue
        Parameters
        ----------
        issue_num

        Returns
        -------
        Recommended library
        """
        # Get Issue
        issue = todo.get_issue(self.repo_owner, self.repo_name, issue_num)
        # TODO: Consider adding project description for context in prompt
        # Ask Chat LLM what libraries it would recommend for issue
        messages = [
            llm.CODER_ROLE,
            {
                "role": "user",
                "content": "In the form of a python "
                "dictionary, what are the top python "
                "libraries I could use for the "
                "following "
                f"ticket?\n{issue.title}\n"
                f"{issue.body}\nRespond in the "
                "form of a python dictionary with "
                "each library name as the "
                "key and a string of two sentences "
                "describing the library "
                "and why to use it for this ticket "
                "as the value.",
            },
        ]
        response: str = llm.chat(messages)
        if not response:
            return None
        response = response[response.find("{") : response.find("}") + 1]
        response = response.replace("'", '"')
        recommendations = json.loads(response)

        # Lookup alternatives
        rec_list = " or ".join(recommendations.keys())
        # TODO: Do this with a web search to get current best practices
        alt_messages = [
            llm.CODER_ROLE,
            {
                "role": "user",
                "content": "In the form of a python dictionary, "
                "what are some alternative python "
                f"libraries to using {rec_list}? "
                "Respond in the form of a python "
                "dictionary with each library name as "
                "the key and a string of two "
                "sentences describing the library "
                "and why to use it for this ticket "
                "as the value.",
            },
        ]
        alt_response: str = llm.chat(alt_messages)
        if alt_response:
            alt_response = alt_response[
                alt_response.find("{") : alt_response.find("}") + 1
            ]
            try:
                recommendations.update(json.loads(alt_response))
            except JSONDecodeError as jde:
                logger.error(str(jde))
                logger.debug(
                    "Unable to get library alternatives.\n"
                    f"Messages: {str(alt_messages)}\n"
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

    def recommend_filename(self, issue_num: int) -> str:
        """
        Recommend a filename to create or add to for the issue
        Parameters
        ----------
        issue_num

        Returns
        -------
        Filename
        """
        # Get Issue
        issue = todo.get_issue(self.repo_owner, self.repo_name, issue_num)
        # TODO: Consider adding project description for context in prompt
        # Ask Chat LLM what filename it would recommend for issue
        messages = [
            llm.CODER_ROLE,
            {
                "role": "user",
                "content": "What should I name the python script that "
                f"solves the following issue?\n{issue.title}"
                f"\n{issue.body}\nRespond with just the name of "
                f"the file.",
            },
        ]
        response: str = llm.chat(messages)
        if response:
            response = sanitize_filename(response)
            if response.find(".py") == -1:
                response += ".py"
            return response
        else:
            logger.error(
                f"No file name recommended for issue #: {issue_num}."
                f"Using {TEMP_FILE}."
            )
            return TEMP_FILE

    def write_code(
        self, issue_num: int, file_name: str, lib_name: Optional[str]
    ) -> None:
        """
        Writes code to the file provided (creating if it doesn't exist)
        Parameters
        ----------
        issue_num
        file_name
        lib_name

        Returns
        -------
        None
        """
        # Get Issue
        issue = todo.get_issue(self.repo_owner, self.repo_name, issue_num)

        # Get File
        file_path = (
            self.repo_path.joinpath("src")
            .joinpath(self.repo_name.replace("-", "_"))
            .joinpath(file_name)
        )
        file_contents = ""
        if file_path.exists():
            with open(file_path, "r") as fp:
                file_contents = fp.read()
        file_header = ""
        if file_contents:
            file_header = file_contents[: file_contents.find("def")]
        use_lib = ""
        if lib_name:
            use_lib = f"Use {lib_name} in the solution."

        # TODO: Consider adding project description for context in prompt
        # Ask Chat LLM to provide code for issue
        messages = [
            llm.CODER_ROLE,
            {
                "role": "user",
                "content": "Provide python code for a solution "
                f"to the following issue.\n"
                f"{use_lib}\n"
                f"{issue.title}\n"
                f"{issue.body}\nRespond with just the python code."
                f"{file_header}",
            },
        ]
        response: str = llm.chat(messages)
        if response:
            if file_contents:
                file_contents = add_text_to_module(
                    file_contents,
                    just_the_code(response),
                )
            else:
                file_contents = just_the_code(response)
            with open(file_path, "w") as fp:
                fp.write(file_contents.replace("\r", ""))
            logger.info(f"Added the following to file {file_path}")
            logger.info(f"{file_contents}")
        else:
            logger.warning(f"No response from LLM for messages: {messages}")
            logger.warning("No source code written.")


if __name__ == "__main__":
    code()
