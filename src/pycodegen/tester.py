from typing import List, Optional

import logging
import os
import subprocess
from pathlib import Path

from github.Issue import Issue

from pycodegen import llm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

tests_dir = "tests"
features_dir = "features"
step_def_dir = "functional"


def create_bdd_dirs(repo_path: Path) -> None:
    """
    Add directories for features and step definitions if they don't exist

    Parameters
    ----------
    repo_path

    Returns
    -------
    None
    """
    tests_path = repo_path.joinpath(tests_dir)
    tests_path.joinpath(features_dir).mkdir(parents=True, exist_ok=True)
    tests_path.joinpath(step_def_dir).mkdir(parents=True, exist_ok=True)


def create_feature(repo_path: Path, issue: Issue) -> Path:
    """
    Create feature file from issue
    Parameters
    ----------
    repo_path
    issue

    Returns
    -------
    Feature file path
    """
    feature_name = issue.title.replace(" ", "_") + ".feature"
    feature_file_path = (
        repo_path.joinpath(tests_dir)
        .joinpath(features_dir)
        .joinpath(feature_name)
    )
    indented_issue_body = indent_sub_lines(issue.body)

    if os.path.exists(feature_file_path):
        logger.warning(
            f"Feature file {feature_file_path} already exists. "
            f"Adding scenario(s)."
        )
        with open(feature_file_path, "r") as ffp:
            existing_scenarios = get_scenarios_from_issue_body(ffp.read())
        scenarios = get_scenarios_from_issue_body(indented_issue_body)
        for scenario in scenarios:
            if scenario in existing_scenarios:
                scenarios.remove(scenario)
        if scenarios:
            with open(feature_file_path, "a") as fp:
                fp.write("\n\n  ")
                fp.writelines(scenarios)
        else:
            logger.info("No new scenarios to add.")
    else:
        with open(feature_file_path, "w") as fp:
            fp.write("Feature: " + issue.title + "\n")
            fp.write(indented_issue_body)
    return feature_file_path


def get_scenarios_from_issue_body(issue_body: str) -> List[str]:
    """
    Returns a list of scenarios from the issue body
    Parameters
    ----------
    issue_body

    Returns
    -------
    List of scenarios
    """
    scenarios = []
    scenario_loc = issue_body.find("cenario:")
    if scenario_loc == -1:
        logger.warning(
            "No scenarios found in issue body. Looking for " "'cenario:'."
        )
        return scenarios
    scenario_loc -= 1
    next_scenario_loc = issue_body.find("cenario:", scenario_loc + 9)
    while next_scenario_loc != -1:
        next_scenario_loc -= 1
        scenarios.append(issue_body[scenario_loc:next_scenario_loc])
        scenario_loc = next_scenario_loc
    scenarios.append(issue_body[scenario_loc:])
    return scenarios


def indent_sub_lines(issue_body: str) -> str:
    """
    Indent lines in the issue body that don't start with Feature or Scenario
    Parameters
    ----------
    issue_body

    Returns
    -------
    Issue body with sub lines indented
    """
    # Remove all carriage returns and add back in only "\n"
    issue_lines = issue_body.splitlines(False)
    saw_scenario = False
    for idx, line in enumerate(issue_lines):
        if (
            line.startswith("Feature:")
            or line.startswith("feature:")
            or line.isspace()
            or not line
        ):
            issue_lines[idx] = line + "\n"
            continue
        if line.startswith("Scenario:") or line.startswith("scenario:"):
            issue_lines[idx] = "  " + line + "\n"
            saw_scenario = True
            continue
        if not saw_scenario:
            issue_lines[idx] = "  " + line + "\n"
        else:
            if (
                line.startswith("Given")
                or line.startswith("given")
                or line.startswith("When")
                or line.startswith("when")
                or line.startswith("Then")
                or line.startswith("then")
                or line.startswith("And")
                or line.startswith("and")
            ):
                issue_lines[idx] = "    " + line + "\n"
            else:
                issue_lines[idx] = "      " + line + "\n"

    return "".join(issue_lines)


def create_step_defs(feature_path: Path) -> Optional[Path]:
    """
    Create definition file from feature file
    Args:
        feature_path

    Returns:
        step_def file path
    """
    feat_file_name = os.path.split(feature_path)[1]
    feature_name = feat_file_name[: feat_file_name.find(".")]
    test_filename = "test_" + feature_name + ".py"
    test_root = feature_path.parent.joinpath("..")
    test_path = test_root.joinpath(step_def_dir).joinpath(test_filename)
    try:
        cp_step_def = subprocess.run(
            [
                "pytest-bdd",
                "generate",
                f"{feature_path}",
            ],
            capture_output=True,
        )
        if cp_step_def.returncode == 0:
            with open(test_path, "w") as tp:
                test_body = cp_step_def.stdout.decode("UTF-8", errors="ignore")
                tp.write(test_body.replace("\r", ""))
            fix_step_def_functions(test_path)
            return test_path
        else:
            logger.error(cp_step_def.stderr)
    except FileNotFoundError as err:
        logger.error(err)


def fix_step_def_functions(test_path: Path) -> None:
    """
    Write titles for step def functions
    Args:
        test_path

    Returns:
        None
    """
    with open(test_path, "r") as tp:
        test_lines = tp.readlines()
    test_lines[0].lstrip('"').rstrip('"')
    prompt_base = (
        "Write just the python function title for the following "
        "step def:\n "
    )
    for idx, line in enumerate(test_lines):
        if line.startswith("@scenario('features\\"):
            test_lines[idx] = line.replace(
                "@scenario('features\\", "@scenario('../features/"
            )
        if line.startswith('@scenario("features\\'):
            test_lines[idx] = line.replace(
                '@scenario("features\\', '@scenario("../features/'
            )
        if line.startswith("def _():"):
            step_def = (
                test_lines[idx - 1]
                .replace("@given(", "")
                .replace("@when(", "")
                .replace("@then(", "")
                .replace(")", "")
            )
            prompt = prompt_base + step_def
            response = llm.complete_prompt(prompt=prompt)
            if response:
                response = response.replace("def ", "").replace("():", "")
                test_lines[idx] = line.replace("_", response)

    with open(test_path, "w") as tp:
        tp.writelines(test_lines)
