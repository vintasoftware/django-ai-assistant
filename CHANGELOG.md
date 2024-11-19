# Changelog

This changelog references changes made both to the Django backend, `django-ai-assistant`, and the
frontend TypeScript client, `django-ai-assistant-client`.

!!! note
    The backend and the frontend are versioned together, that is, they have the same version number.
    When you update the backend, you should also update the frontend to the same version.

## 0.1.1 <small>November 19, 2024</small> {id="0.1.1"}

- Fix an `AttributeError` raised in RAG AIAssistants when the `retriever` supports the `invoke` call
only with the query string as `input`.

## 0.1.0 <small>October 11, 2024</small> {id="0.1.0"}

- Refactor the code to use LangGraph instead of LangChain LCEL
  (except for RAG functionality, see the `get_history_aware_retriever` method).
- Store all messages in the `Thread` model, including tool calls and their outputs.
- Allow separation of threads per assistant: `assistant_id` in the `Thread` model.
- New `updateThread` function from `useThreadList` hook.
- Improved examples:
    - Add markdown rendering to HTMX example.
    - Better Movie Recommendation example.
    - Better Tour Guide example.

## 0.0.4 <small>July 5, 2024</small> {id="0.0.4"}

- Fix frontend README.

## 0.0.3 <small>July 5, 2024</small> {id="0.0.3"}

- Less restrictive Python version in pyproject.toml. Support future Python versions.

## 0.0.2 <small>June 28, 2024</small> {id="0.0.2"}

- Add support for Django 4.2 LTS
- Add support for Python 3.10 and 3.11

## 0.0.1 <small>June 25, 2024</small> {id="0.0.1"}

- Initial release
