# Contributing

We can always use your help to improve Django AI Assistant! Please feel free to tackle existing [issues](https://github.com/vintasoftware/django-ai-assistant/issues). If you have a new idea, please create a thread on [Discussions](https://github.com/vintasoftware/django-ai-assistant/discussions).

Please follow this guide to learn more about how to develop and test the project locally, before opening a pull request.

## Local Dev Setup

### Clone the repo

`git clone git@github.com:vintasoftware/django-ai-assistant.git`

### Set up a virtualenv, optionally set up nvm, and activate your environment(s)

You can use [pyenv](https://github.com/pyenv/pyenv), [pipenv](https://github.com/pypa/pipenv/blob/main/docs/installation.md), vanilla venvs or the tool of your choice.

For installing Node, we recommend [NVM](https://github.com/nvm-sh/nvm).

### Install dependencies

#### Backend

`poetry install`

#### Frontend

```bash
cd frontend
npm install
```

### Install pre-commit hooks

`pre-commit install`

It's critical to run the pre-commit hooks before pushing your code to follow the project's code style, and avoid linting errors.

### Developing with the example project

Run the frontend project in build:watch mode:

```bash
cd frontend
npm run build:watch
```

Then follow the instructions in the [example README](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#readme).

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
