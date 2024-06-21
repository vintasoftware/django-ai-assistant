# Example

Django AI Assistant examples. This is a Django project that integrates with Django AI Assistant library.

Most examples are inside a React frontend, but there is also a HTMX example.

## Installation

Go to project root, then frontend dir and build the frontend library:

```bash
cd ..  # back to project root directory
cd frontend
npm install
npm run build
```

Then use `npm link` to link the frontend library to the example project:

```bash
cd frontend
npm link
```

Go to the example project to finish the link with the frontend library:

```bash
cd ..  # back to project root directory
cd example
npm install
npm link django-ai-assistant-client
```

Run the example Webpack devserver to build the React frontend:

```bash
# in example directory
npm run start
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
- [Weather](https://www.weatherapi.com/)
- [Tavily](https://app.tavily.com/)
- [Firecrawl](https://www.firecrawl.dev/)

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

Access the Django admin at `http://localhost:8000/admin/` and log in with the superuser account.

## Usage

Access the example project at `http://localhost:8000/`.

