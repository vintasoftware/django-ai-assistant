from django.contrib.auth.models import User

import pytest
from model_bakery import baker

from django_ai_assistant.exceptions import (
    AIAssistantNotDefinedError,
    AIUserNotAllowedError,
)
from django_ai_assistant.helpers import use_cases
from django_ai_assistant.helpers.assistants import AIAssistant
from django_ai_assistant.langchain.tools import BaseModel, Field, method_tool
from django_ai_assistant.models import Message, Thread


# Set up


@pytest.fixture(scope="module", autouse=True)
def setup_assistants():
    # Clear the registry before the tests in the module
    AIAssistant.clear_cls_registry()

    # Define the assistant class inside the fixture to ensure registration
    class TemperatureAssistant(AIAssistant):
        id = "temperature_assistant"  # noqa: A003
        name = "Temperature Assistant"
        instructions = "You are a temperature bot."
        model = "gpt-4o"

        def get_instructions(self):
            return self.instructions + " Today is 2024-06-09."

        @method_tool
        def fetch_current_temperature(self, location: str) -> str:
            """Fetch the current temperature data for a location"""
            return "32 degrees Celsius"

        class FetchForecastTemperatureInput(BaseModel):
            location: str
            dt_str: str = Field(description="Date in the format 'YYYY-MM-DD'")

        @method_tool(args_schema=FetchForecastTemperatureInput)
        def fetch_forecast_temperature(self, location: str, dt_str: str) -> str:
            """Fetch the forecast temperature data for a location"""
            return "35 degrees Celsius"

    yield
    # Clear the registry after the tests in the module
    AIAssistant.clear_cls_registry()


def fake_permission_func(**kwargs):
    return False


@pytest.fixture()
def use_fake_permissions(settings):
    settings.AI_ASSISTANT_CAN_RUN_ASSISTANT = "tests.test_use_cases.fake_permission_func"
    settings.AI_ASSISTANT_CAN_CREATE_THREAD_FN = "tests.test_use_cases.fake_permission_func"


# Assistant tests


def test_get_cls_returns_assistant_cls():
    assistant_id = "temperature_assistant"
    user = User()

    assistant_cls = use_cases.get_cls(assistant_id, user)

    assert assistant_cls.id == assistant_id


def test_get_cls_raises_error_when_assistant_not_defined():
    assistant_id = "not_defined"
    user = User()

    with pytest.raises(AIAssistantNotDefinedError):
        use_cases.get_cls(assistant_id, user)


def test_get_cls_raises_error_when_user_not_allowed(use_fake_permissions):
    assistant_id = "temperature_assistant"
    user = User()

    with pytest.raises(AIUserNotAllowedError):
        use_cases.get_cls(assistant_id, user)


def test_get_single_assistant_info_returns_info():
    assistant_id = "temperature_assistant"
    user = User()

    info = use_cases.get_single_assistant_info(assistant_id, user)

    assert info["id"] == "temperature_assistant"
    assert info["name"] == "Temperature Assistant"


def test_get_single_assistant_info_raises_exception_when_assistant_not_defined():
    assistant_id = "not_defined"
    user = User()

    with pytest.raises(AIAssistantNotDefinedError):
        use_cases.get_single_assistant_info(assistant_id, user)


def test_get_single_assistant_info_raises_exception_when_user_not_allowed(use_fake_permissions):
    assistant_id = "temperature_assistant"
    user = User()

    with pytest.raises(AIUserNotAllowedError):
        use_cases.get_single_assistant_info(assistant_id, user)


def test_get_assistants_info_returns_info():
    user = User()

    info = use_cases.get_assistants_info(user)

    assert info[0].id == "temperature_assistant"
    assert info[0].name == "Temperature Assistant"
    assert len(info) == 1


# Message tests


@pytest.mark.django_db(transaction=True)
@pytest.mark.vcr
def test_create_message():
    user = baker.make(User)
    thread = baker.make(Thread, created_by=user)
    response = use_cases.create_message(
        "temperature_assistant",
        thread,
        user,
        "Hello, will I have to use my umbrella in Lisbon tomorrow?",
    )

    assert response == {
        "input": "Hello, will I have to use my umbrella in Lisbon tomorrow?",
        "history": [],
        "output": "The forecast for Lisbon tomorrow is 35°C, which is quite warm and unlikely to involve rain. You probably won't need an umbrella.",
    }


@pytest.mark.django_db(transaction=True)
def test_create_message_raises_exception_when_user_not_allowed():
    user = baker.make(User)
    thread = baker.make(Thread)

    with pytest.raises(AIUserNotAllowedError):
        use_cases.create_message(
            "temperature_assistant",
            thread,
            user,
            "Hello, will I have to use my umbrella in Lisbon tomorrow?",
        )


# Thread tests


@pytest.mark.django_db(transaction=True)
def test_create_thread():
    user = baker.make(User)
    response = use_cases.create_thread("My thread", user)

    assert response.name == "My thread"
    assert response.created_by == user


@pytest.mark.django_db(transaction=True)
def test_create_thread_raises_exception_when_user_not_allowed(use_fake_permissions):
    user = baker.make(User)

    with pytest.raises(AIUserNotAllowedError):
        use_cases.create_thread("My thread", user)


@pytest.mark.django_db(transaction=True)
def test_get_single_thread():
    user = baker.make(User)
    thread = baker.make(Thread, created_by=user)
    response = use_cases.get_single_thread(thread.id, user)

    assert response == thread


@pytest.mark.django_db(transaction=True)
def test_get_single_thread_raises_exception_when_user_not_allowed():
    user = baker.make(User)
    thread = baker.make(Thread)

    with pytest.raises(AIUserNotAllowedError):
        use_cases.get_single_thread(thread.id, user)


@pytest.mark.django_db(transaction=True)
def test_get_threads():
    user = baker.make(User)
    baker.make(Thread, created_by=user, _quantity=3)
    response = use_cases.get_threads(user)

    assert len(response) == 3


@pytest.mark.django_db(transaction=True)
def test_get_threads_does_not_list_other_users_threads():
    user = baker.make(User)
    baker.make(Thread, _quantity=3)
    response = use_cases.get_threads(user)

    assert len(response) == 0


@pytest.mark.django_db(transaction=True)
def test_update_thread():
    user = baker.make(User)
    thread = baker.make(Thread, created_by=user)
    response = use_cases.update_thread(thread, "My updated thread", user)

    assert response.name == "My updated thread"


@pytest.mark.django_db(transaction=True)
def test_update_thread_raises_exception_when_user_not_allowed():
    user = baker.make(User)
    thread = baker.make(Thread)

    with pytest.raises(AIUserNotAllowedError):
        use_cases.update_thread(thread, "My updated thread", user)


@pytest.mark.django_db(transaction=True)
def test_delete_thread():
    user = baker.make(User)
    thread = baker.make(Thread, created_by=user)
    use_cases.delete_thread(thread, user)

    assert not Thread.objects.filter(id=thread.id).exists()


@pytest.mark.django_db(transaction=True)
def test_delete_thread_raises_exception_when_user_not_allowed():
    user = baker.make(User)
    thread = baker.make(Thread)

    with pytest.raises(AIUserNotAllowedError):
        use_cases.delete_thread(thread, user)


# Thread message tests


@pytest.mark.django_db(transaction=True)
def test_get_thread_messages():
    user = baker.make(User)
    thread = baker.make(Thread, created_by=user)
    baker.make(
        Message, message={"type": "human", "data": {"content": "hi"}}, thread=thread, _quantity=3
    )
    response = use_cases.get_thread_messages(thread.id, user)

    assert len(response) == 3


@pytest.mark.django_db(transaction=True)
def test_get_thread_messages_raises_exception_when_user_not_allowed():
    user = baker.make(User)
    thread = baker.make(Thread)
    baker.make(
        Message, message={"type": "human", "data": {"content": "hi"}}, thread=thread, _quantity=3
    )

    with pytest.raises(AIUserNotAllowedError):
        use_cases.get_thread_messages(thread.id, user)


@pytest.mark.django_db(transaction=True)
def test_create_thread_message_as_user():
    user = baker.make(User)
    thread = baker.make(Thread, created_by=user)
    use_cases.create_thread_message_as_user(thread.id, "Hello, how are you?", user)

    assert Message.objects.filter(thread=thread).count() == 1


@pytest.mark.django_db(transaction=True)
def test_create_thread_message_as_user_raises_exception_when_user_not_allowed():
    user = baker.make(User)
    thread = baker.make(Thread)

    with pytest.raises(AIUserNotAllowedError):
        use_cases.create_thread_message_as_user(thread.id, "Hello, how are you?", user)


@pytest.mark.django_db(transaction=True)
def test_delete_message():
    user = baker.make(User)
    thread = baker.make(Thread, created_by=user)
    message = baker.make(Message, thread=thread)
    use_cases.delete_message(message, user)

    assert not Message.objects.filter(id=message.id).exists()


@pytest.mark.django_db(transaction=True)
def test_delete_message_raises_exception_when_user_not_allowed():
    user = baker.make(User)
    message = baker.make(Message)

    with pytest.raises(AIUserNotAllowedError):
        use_cases.delete_message(message, user)
