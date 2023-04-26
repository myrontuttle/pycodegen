# pycodegen

[![Build status](https://github.com/myrontuttle/pycodegen/workflows/build/badge.svg?branch=main&event=push)](https://github.com/myrontuttle/pycodegen/actions?query=workflow%3Abuild)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/myrontuttle/pycodegen/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/myrontuttle/pycodegen/blob/main/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/myrontuttle/pycodegen/releases)
[![License](https://img.shields.io/github/license/myrontuttle/pycodegen)](https://github.com/myrontuttle/pycodegen/blob/main/LICENSE)

Python Code Generator

## Dependencies

- [Python](https://www.python.org/) 3.9

## Installation

```bash
pip install pycodegen
```

or install with `PDM`

```bash
pdm add pycodegen
```

or install with `pipx1`

```bash
pipx install git+https://github.com/myrontuttle/pycodegen.git
```

## Usage

```python
import pycodegen

coder = Coder(repo_owner, repo_name)
response_code = coder.open_issue(issue_num)
# Work on issue
response_code = coder.finish_issue(commit_msg)
```

If installed with pipx
```bash
coder start <githubaccount> <project> [-i <issuenumber>]
# Work on issue
coder finish <githubaccount> <project> [-m "<commit message>"]
```

### Makefile usage

[`Makefile`](https://github.com/myrontuttle/pycodegen/blob/main/Makefile) contains a lot of functions for faster development.

<details>
<summary>1. Install all dependencies and pre-commit hooks</summary>
<p>

Install requirements:

```bash
make install
```

Update PDM

```bash
make update
```

Update all dev libraries to the latest version using one command

```bash
make update-dev-deps
```

</p>
</details>

<details>
<summary>2. Codestyle Formatting</summary>
<p>

Automatic formatting uses `autoflake`, `pyupgrade`, `isort` and `black`.

```bash
make format
```

Codestyle checks only, without rewriting files:

```bash
make check-codestyle
```

> Note: `check-codestyle` uses `isort`, `black` and `ruff` library

</p>
</details>

<details>
<summary>3. Code security</summary>
<p>

```bash
make check-security
```

This command launches `PDM` integrity checks as well as identifies security issues with `Bandit`.

```bash
make check-security
```

</p>
</details>

<details>
<summary>4. Type checks</summary>
<p>

Run `mypy` static type checker

```bash
make mypy
```

</p>
</details>

<details>
<summary>5. Tests with coverage badges</summary>
<p>

Run `pytest`

```bash
make test
```

</p>
</details>

<details>
<summary>6. All checks</summary>
<p>

Run all checks:

```bash
make check-all
```

the same as:

```bash
make check-style && make mypy && make check-safety && make test
```

</p>
</details>

<details>
<summary>7. Deploy</summary>
<p>
Prepare to deploy

```bash
make prepare-deploy
```

</p>
</details>

<details>
<summary>8. Cleanup</summary>
<p>
Delete pycache files

```bash
make pycache-remove
```

Remove package build

```bash
make build-remove
```

Remove .mypycache

```bash
make mypycache-remove
```

Or to remove all above run:

```bash
make cleanup
```

</p>
</details>

## Reference
Built using project template [here](https://github.com/myrontuttle/python-copier-template).
