# Contributing

We can always use your help to improve Django AI Assistant! Please feel free to tackle existing [issues](https://github.com/vintasoftware/django-ai-assistant/issues). If you have a new idea, please create a thread on [Discussions](https://github.com/vintasoftware/django-ai-assistant/discussions).

Please follow this guide to learn more about how to develop and test the project locally, before opening a pull request.

## Local Dev Setup

### Clone the repo

```bash
git clone git@github.com:vintasoftware/django-ai-assistant.git
```

### Set up a virtualenv, optionally set up nvm, and activate your environment(s)

You can use [pyenv](https://github.com/pyenv/pyenv), [pipenv](https://github.com/pypa/pipenv/blob/main/docs/installation.md), vanilla venvs or the tool of your choice.

For installing Node, we recommend [NVM](https://github.com/nvm-sh/nvm).

### Install dependencies

#### Backend

Go to the project root and install the Python dependencies:

```bash
poetry install
```

#### Frontend

Go to the frontend directory and install the Node dependencies:

```bash
cd frontend
pnpm install
```

### Install pre-commit hooks

```bash
pre-commit install
```

It's critical to run the pre-commit hooks before pushing your code to follow the project's code style, and avoid linting errors.

### Developing with the example project

Run the frontend project in `build:watch` mode:

```bash
cd frontend
pnpm run build:watch
```

Go to the example project, install the dependencies, and link the frontend project:

```bash
cd ..  # back to project root directory
cd example
pnpm install
pnpm remove django-ai-assistant-client  # remove the distributed package to use the local one
pnpm link ../frontend
```

Then follow the instructions in the [example README](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#running) to run the example project.

## Tests

Run tests with:

```bash
poetry run pytest
```

The tests use `pytest-vcr` to record and replay HTTP requests to AI models.

If you're implementing a new test that needs to call a real AI model, you need to set the `OPENAI_API_KEY` environment variable on root `.env` file.
Then, you will run the tests in record mode:

```bash
poetry run pytest --record-mode=once
```

## Documentation

We use [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) to generate the documentation from markdown files.
Check the files in the `docs` directory.

To run the documentation locally, you need to run:

```bash
poetry run mkdocs serve
```

## Release

!!! info
    The backend and the frontend are versioned together, that is, they should have the same version number.

To release and publish a new version, follow these steps:

1. Update the version in `pyproject.toml` and `frontend/package.json`.
2. Update the changelog in `CHANGELOG.md`.
3. Open a PR with the changes.
4. Once the PR is merged, run the [Release GitHub Action](https://github.com/vintasoftware/django-ai-assistant/actions/workflows/release.yml) to create a draft release.
5. Review the draft release, ensure the description has at least the associated changelog entry, and publish it.
6. Once the review is publish, the [Publish GitHub Action](https://github.com/vintasoftware/django-ai-assistant/actions/workflows/publish.yml) will automatically run to publish the new version to [PyPI](https://pypi.org/project/django-ai-assistant) and [npm](https://www.npmjs.com/package/django-ai-assistant-client). Check the logs to ensure the publication was successful.