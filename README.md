# eq-cims-management-ui

[![Build Status](https://github.com/ONSdigital/eq-cims-management-ui/actions/workflows/ci.yml/badge.svg)](https://github.com/ONSdigital/eq-cir-management-ui/actions/workflows/ci.yml)
[![Build Status](https://github.com/ONSdigital/eq-cims-management-ui/actions/workflows/mega-linter.yml/badge.svg)](https://github.com/ONSdigital/eq-cir-management-ui/actions/workflows/mega-linter.yml)
[![Build Status](https://github.com/ONSdigital/eq-cims-management-ui/actions/workflows/codeql.yml/badge.svg)](https://github.com/ONSdigital/eq-cir-management-ui/actions/workflows/codeql.yml)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![poetry-managed](https://img.shields.io/badge/poetry-managed-blue)](https://python-poetry.org/)
[![License - MIT](https://img.shields.io/badge/licence%20-MIT-1ac403.svg)](https://github.com/ONSdigital/eq-cims-management-ui/blob/main/LICENSE)

eq-cims-management-ui

---

## Table of Contents

[//]: # ":TODO: Enable link checking once https://github.com/tcort/markdown-link-check/issues/250 is resolved."

<!-- markdown-link-check-disable -->

- [Getting Started](#getting-started)
    - [Pre-requisites](#pre-requisites)
    - [Installation](#installation)
- [Development](#development)
    - [Run Application with Database](#run-application-with-database)
    - [Run All Tests](#run-all-tests)
    - [Run Unit Tests with Coverage](#run-unit-tests-with-coverage)
    - [Run Functional Tests](#run-functional-tests)
    - [Linting and Formatting](#linting-and-formatting)
- [Contributing](#contributing)
- [License](#license)
    <!-- markdown-link-check-enable -->

## Getting Started

To get a local copy up and running, follow these simple steps.

### Pre-requisites

Ensure you have the following installed:

1. **Python**: Version specified in `.python-version`. We recommend using [pyenv](https://github.com/pyenv/pyenv) for
    managing Python versions.
2. **[Poetry](https://python-poetry.org/)**: This is used to manage package dependencies and virtual
    environments.
3. **[Docker](https://docs.docker.com/engine/install/)**
4. **Operation System**: Ubuntu/MacOS

### Installation

1. Clone the repository and install the required dependencies.

    ```bash
    git clone https://github.com/ONSdigital/eq-cims-management-ui.git
    ```

2. Install dependencies

    [Poetry](https://python-poetry.org/) is used to manage dependencies in this project. For more information, read
    the [Poetry documentation](https://python-poetry.org/).

    To install all dependencies, including development dependencies, run:

    ```bash
    make install-dev
    ```

    To install only production dependencies, run:

    ```bash
    make install
    ```

    To install the ONS Design System using node (fuller details below):

    ```bash
    nvm install
    nvm use
    ```

    then run:

    ```bash
    npm install
    ```

    to add the Design System.

3. Run the application

    ```bash
    make run
    ```

## Development

Get started with development by running the following commands.
Before proceeding, make sure you have the development dependencies installed using the `make install-dev` command.

A Makefile is provided to simplify common development tasks. To view all available commands, run:

```bash
make
```

To run the UI in debug mode, you can add a root `.env` file, and add the setting `FLASK_DEBUG=1`.

## ONS Design System

The ONS design system needs to be installed using [npm](https://www.npmjs.com/).
To install the ONS Design System npm package you will need to install [node.js](https://nodejs.org/en/).
To do this, use the following commands:

```bash
nvm install
nvm use
```

Then:

- Run `npm install` from the project root directory.

This will install the design system into a local node_modules folder.
The `@ons/design-system` package is then automatically added to the jinja configuration.

The used design system version is pulled directly from the version in package.json.
A fallback version is set in `templates/base.html`.

### Run Application with Database

To run the application with a local database, you will need to complete the following steps:

- Create or update a `.env` file to contain the following environment variable:

```text
FIRESTORE_EMULATOR_HOST="localhost:8080"
```

- To run the application locally with a Firestore emulator, use the following commands:

```bash
make dev-compose-up
make run
```

- Alternatively, you can use the following commands to run both the application and Firestore emulator with Docker:

```bash
docker-compose build
docker-compose up -d
```

### Run All Tests

To run all functional and unit tests, run the following commands (*Note: Functional tests require an instance
of the Firestore Emulator to be running*):

```bash
make dev-compose-up
```

```bash
make test
```

### Run Unit Tests with Coverage

The unit tests are written using the [pytest](https://docs.pytest.org/en/stable/) framework. To run the tests and check
coverage, run:

```bash
make test-unit
```

### Run Functional Tests

The functional tests are written in Python using the Playwright framework. Functional tests require a running
instance of the Firestore Emulator. To run the functional tests, use the following commands:

```bash
make dev-compose-up
```

```bash
make test-functional
```

### Linting and Formatting

Various tools are used to lint and format the code in this project.

#### Python

The project uses [Ruff](https://github.com/astral-sh/ruff), [pylint](https://pylint.pycqa.org/en/latest/index.html)
and [black](https://black.readthedocs.io/en/stable/) for linting and formatting of the Python code.

The tools are configured using the `pyproject.toml` file.

To lint the Python code, run:

```bash
make lint
```

To auto-format the Python code, and correct fixable linting issues, run:

```bash
make format
```

#### MegaLinter (Lint/Format non-python files)

[MegaLinter](https://github.com/oxsecurity/megalinter) is utilised to lint the non-python files in the project.
It offers a single interface to execute a suite of linters for multiple languages and formats, ensuring adherence to
best practices and maintaining consistency across the repository without the need to install each linter individually.

MegaLinter examines various file types and tools, including GitHub Actions, Shell scripts, Dockerfile, etc. It is
configured using the `.mega-linter.yml` file.

To run MegaLinter, ensure you have **Docker** installed on your system.

> Note: The initial run may take some time to download the Docker image. However, subsequent executions will be
> considerably faster due to Docker caching. :rocket:

To start the linter and automatically rectify fixable issues, run:

```bash
make megalint
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

See [LICENSE](LICENSE) for details.
