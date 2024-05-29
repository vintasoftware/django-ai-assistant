import openai_responses
import pytest
from openai_responses import OpenAIMock

from django_ai_assistant.ai.sync import sync_assistants
from django_ai_assistant.helpers.assistants import ASSISTANT_DEF_CLS_REGISTRY, AIAssistant
from django_ai_assistant.models import Assistant
from tests.client import init_openai
from tests.utils import DictSubSet


class WeatherAssistant(AIAssistant):
    name = "Weather Assistant"
    instructions = "You are a weather bot."
    fns = ()
    model = "gpt-4"


class TimeAssistant(AIAssistant):
    name = "Time Assistant"
    instructions = "You are a time bot."
    fns = ()
    model = "gpt-4o"


class WeatherAssistantV2(AIAssistant):
    name = "Weather Assistant V2"
    instructions = "You are a weather bot."
    fns = ()
    model = "gpt-4o"


@pytest.mark.django_db
@openai_responses.mock()
def test_sync_assistants(openai_mock: OpenAIMock):
    # Create initial data in OpenAI:
    client = init_openai()
    openai_assistant_0 = client.beta.assistants.create(
        instructions="You are a weather bot.",
        model="gpt-3.5-turbo",  # model out of sync w/ class, will be updated
        name="Weather Bot",  # name out of sync w/ class, will be updated
    )
    openai_assistant_1 = client.beta.assistants.create(
        instructions="You are a time bot.",
        model="gpt-3.5-turbo",  # model out of sync w/ class, will be updated
        name="Time Bot",  # name out of sync w/ class, will be updated
    )

    # Create initial data in Django:
    ASSISTANT_DEF_CLS_REGISTRY.clear()
    ASSISTANT_DEF_CLS_REGISTRY.update(
        {
            "WeatherAssistant": WeatherAssistant,
            "TimeAssistant": TimeAssistant,
            "WeatherAssistantV2": WeatherAssistantV2,
        }
    )

    assistant_0 = Assistant.objects.create(
        openai_id=openai_assistant_0.id,
        name="Weather Bot",  # name out of sync w/ class, will be updated
        slug="WeatherAssistant",
    )
    assistant_1 = Assistant.objects.create(
        openai_id=openai_assistant_1.id,
        name="Time Bot",  # name out of sync w/ class, will be updated
        slug="TimeAssistant",
    )
    assistant_2 = Assistant.objects.create(
        name="Weather Bot V2",  # name out of sync w/ class, will be updated
        slug="WeatherAssistantV2",
    )

    # Sync the assistants:
    sync_assistants()

    # Check the post-sync data in OpenAI:
    openai_assistants_dict = {a.id: a for a in client.beta.assistants.list()}
    assert len(openai_assistants_dict) == 3
    assistant_0.refresh_from_db()
    assistant_1.refresh_from_db()
    assistant_2.refresh_from_db()
    assert openai_assistant_0.id in openai_assistants_dict
    assert openai_assistant_1.id in openai_assistants_dict
    assert assistant_2.openai_id in openai_assistants_dict
    assert openai_assistants_dict[openai_assistant_0.id].to_dict() == DictSubSet(
        {
            "name": "Weather Assistant",
            "instructions": "You are a weather bot.",
            "model": "gpt-4",
        }
    )

    assert openai_assistants_dict[openai_assistant_1.id].to_dict() == DictSubSet(
        {
            "name": "Time Assistant",
            "instructions": "You are a time bot.",
            "model": "gpt-4o",
        }
    )
    assert openai_assistants_dict[assistant_2.openai_id].to_dict() == DictSubSet(
        {
            "name": "Weather Assistant V2",
            "instructions": "You are a weather bot.",
            "model": "gpt-4o",
        }
    )

    # Check the post-sync data in Django:
    assert assistant_0.openai_id == openai_assistant_0.id
    assert assistant_1.openai_id == openai_assistant_1.id
    assert assistant_0.name == WeatherAssistant.name
    assert assistant_1.name == TimeAssistant.name
    assert assistant_2.name == WeatherAssistantV2.name
    assert assistant_0.cls_synced_at is not None
    assert assistant_1.cls_synced_at is not None
    assert assistant_2.cls_synced_at is not None
    assert assistant_0.openai_synced_at is not None
    assert assistant_1.openai_synced_at is not None
    assert assistant_2.openai_synced_at is not None
