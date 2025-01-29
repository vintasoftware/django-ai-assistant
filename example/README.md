# Example

Django AI Assistant examples. This is a Django project that integrates with Django AI Assistant library.

Most examples are inside a React frontend, but there is also a HTMX example.

## Installation

Go to the example project, install its Node dependencies, and run the example Webpack devserver to build the React frontend:

```bash
# in example directory
cd example
pnpm install
pnpm run start
```

Install the example project Python dependencies:

```bash
cd ..  # back to project root directory
poetry install
```

Create a `.env` file at the example directory:

```bash
# in example directory
cp .env.example .env
```

Fill the `.env` file with the necessary API keys. You'll need accounts on:

- [OpenAI](https://platform.openai.com/)
- [Weather API](https://www.weatherapi.com/)
- [Brave Search API](https://app.tavily.com/)
- [Jina Reader API](https://jina.ai/)

Activate the poetry shell:
    
```bash
poetry shell
```

Run Django migrations:

```bash
# in example directory
python manage.py migrate
```

Create a superuser:

```bash
# in example directory
python manage.py createsuperuser
```

Run the Django server:

```bash
# in example directory
python manage.py runserver
```

[Optional] To use the RAG example, run:

```bash
# in example directory
python manage.py fetch_django_docs
```

Access the Django admin at `http://localhost:8000/admin/` and log in with the superuser account.

## Usage

Access the example project at `http://localhost:8000/`.

## VSCode

Fix the Python path in your `<project-root>/.vscode/settings.json` to fix the Python import linting:

```json
{
    // ...
    "python.analysis.extraPaths": [
        "example/"
    ]
}
```
