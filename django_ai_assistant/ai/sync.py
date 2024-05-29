from typing import cast

from openai import OpenAI

from django_ai_assistant.conf import settings
from django_ai_assistant.exceptions import AIAssistantClsNotDefinedError
from django_ai_assistant.helpers.assistants import (
    ASSISTANT_DEF_CLS_REGISTRY,
    sync_assistant_def_cls_with_django_assistant,
    sync_assistant_in_openai,
)
from django_ai_assistant.models import Assistant


def sync_assistants(client: OpenAI | None = None):
    """
    Sync the assistant classes registered with `@register_assistant` decorator
    with Django models and OpenAI's API.
    Create new assistants in OpenAI and store their OpenAI IDs
    in the database in new Django model instances.
    Update existing assistants in OpenAI and Django.
    Does not delete any assistants in OpenAI and Django,
    even if they are not in the registry anymore.

    :returns a list of OpenAI IDs that were synced.
    """
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))
    synced_openai_ids = []

    # Update or create existing assistants in Django:
    for assistant_def_cls in ASSISTANT_DEF_CLS_REGISTRY.values():
        sync_assistant_def_cls_with_django_assistant(assistant_def_cls)

    # Update or create assistants in OpenAI:
    for django_assistant in Assistant.objects.order_by("id"):
        try:
            sync_assistant_in_openai(django_assistant, client=client)
        except AIAssistantClsNotDefinedError:
            # Ignore assistants that are not in the registry
            continue
        synced_openai_ids.append(django_assistant.openai_id)

    return synced_openai_ids
