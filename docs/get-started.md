---
search:
  boost: 2 
---

# Get started

## Prerequisites

- Python: <a href="https://pypi.org/project/django-ai-assistant" target="_blank"><img src="https://img.shields.io/pypi/pyversions/django-ai-assistant.svg?color=%2334D058" alt="Supported Python versions"></a>
- Django: <a href="https://pypi.org/project/django-ai-assistant" target="_blank"><img src="https://img.shields.io/pypi/frameworkversions/django/django-ai-assistant.svg" alt="Supported Django versions"></a>

## How to install

Install Django AI Assistant package, specifying which provider you wish to install (in the example below it'll install the required dependencies for using OpenAI utils):

```bash
pip install django-ai-assistant[openai]
```

The options for provider are:
- `openai`
- `anthropic`
- `google`

Add Django AI Assistant to your Django project's `INSTALLED_APPS`:

```python title="myproject/settings.py"
INSTALLED_APPS = [
    ...
    'django_ai_assistant',
    ...
]
```

Run the migrations:

```bash
python manage.py migrate
```

Learn how to use the package in the [Tutorial](tutorial.md) section.
