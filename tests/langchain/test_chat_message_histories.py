import pytest
from langchain_core.messages import AIMessage, HumanMessage

from django_ai_assistant.langchain.chat_message_histories import DjangoChatMessageHistory
from django_ai_assistant.models import Message, Thread


@pytest.fixture()
def thread_aaa(db):
    return Thread.objects.create(name="AAA")


@pytest.fixture()
def thread_bbb(db):
    return Thread.objects.create(name="BBB")


def test_add_messages(thread_aaa, thread_bbb):
    thread = Thread.objects.get(name="AAA")
    other_thread = Thread.objects.get(name="BBB")

    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    message_history.add_messages(
        [HumanMessage(content="Hello, world!"), AIMessage(content="Hi! How are you?")]
    )

    assert thread.messages.count() == 2
    message_0 = thread.messages.order_by("created_at").first()
    assert message_0.message["data"]["content"] == "Hello, world!"
    assert message_0.message["type"] == "human"
    message_1 = thread.messages.order_by("created_at").last()
    assert message_1.message["data"]["content"] == "Hi! How are you?"
    assert message_1.message["type"] == "ai"
    assert other_thread.messages.count() == 0


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_aadd_messages(thread_aaa, thread_bbb):
    thread = await Thread.objects.aget(name="AAA")
    other_thread = await Thread.objects.aget(name="BBB")

    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    await message_history.aadd_messages(
        [HumanMessage(content="Hello, world!"), AIMessage(content="Hi! How are you?")]
    )

    assert await thread.messages.acount() == 2
    message_0 = await thread.messages.order_by("created_at").afirst()
    assert message_0.message["data"]["content"] == "Hello, world!"
    assert message_0.message["type"] == "human"
    message_1 = await thread.messages.order_by("created_at").alast()
    assert message_1.message["data"]["content"] == "Hi! How are you?"
    assert message_1.message["type"] == "ai"
    assert await other_thread.messages.acount() == 0


def test_remove_messages(thread_aaa, thread_bbb):
    thread = Thread.objects.get(name="AAA")
    other_thread = Thread.objects.get(name="BBB")

    Message.objects.bulk_create(
        [
            Message(thread=thread, message={"data": {"content": "Hello, world!"}, "type": "human"}),
            Message(thread=thread, message={"data": {"content": "Hi! How are you?"}, "type": "ai"}),
            Message(thread=other_thread, message={"data": {"content": "Olá!"}, "type": "human"}),
            Message(
                thread=other_thread, message={"data": {"content": "Olá! Como vai?"}, "type": "ai"}
            ),
            Message(
                thread=other_thread,
                message={"data": {"content": "Bem, está quente em Recife?"}, "type": "human"},
            ),
        ]
    )

    assert thread.messages.count() == 2

    messages = thread.messages.order_by("created_at")
    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    message_history.remove_messages([messages[0].id])

    assert messages.count() == 1
    assert messages.first().message["data"]["content"] == "Hi! How are you?"
    assert other_thread.messages.count() == 3


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_aremove_messages(thread_aaa, thread_bbb):
    thread = await Thread.objects.aget(name="AAA")
    other_thread = await Thread.objects.aget(name="BBB")

    await Message.objects.abulk_create(
        [
            Message(thread=thread, message={"data": {"content": "Hello, world!"}, "type": "human"}),
            Message(thread=thread, message={"data": {"content": "Hi! How are you?"}, "type": "ai"}),
            Message(thread=other_thread, message={"data": {"content": "Olá!"}, "type": "human"}),
            Message(
                thread=other_thread, message={"data": {"content": "Olá! Como vai?"}, "type": "ai"}
            ),
            Message(
                thread=other_thread,
                message={"data": {"content": "Bem, está quente em Recife?"}, "type": "human"},
            ),
        ]
    )

    assert await thread.messages.acount() == 2

    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    await message_history.aremove_messages(
        [(await thread.messages.order_by("created_at").afirst()).id]
    )

    assert await thread.messages.acount() == 1
    assert (await thread.messages.order_by("created_at").afirst()).message["data"][
        "content"
    ] == "Hi! How are you?"
    assert await other_thread.messages.acount() == 3


def test_get_messages(thread_aaa, thread_bbb):
    thread = Thread.objects.get(name="AAA")
    other_thread = Thread.objects.get(name="BBB")

    Message.objects.bulk_create(
        [
            Message(thread=thread, message={"data": {"content": "Hello, world!"}, "type": "human"}),
            Message(thread=thread, message={"data": {"content": "Hi! How are you?"}, "type": "ai"}),
            Message(thread=other_thread, message={"data": {"content": "Olá!"}, "type": "human"}),
            Message(
                thread=other_thread, message={"data": {"content": "Olá! Como vai?"}, "type": "ai"}
            ),
            Message(
                thread=other_thread,
                message={"data": {"content": "Bem, está quente em Recife?"}, "type": "human"},
            ),
        ]
    )

    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    messages = message_history.get_messages()
    other_message_history = DjangoChatMessageHistory(thread_id=other_thread.id)
    other_messages = other_message_history.get_messages()

    assert len(messages) == 2
    assert messages[0].content == "Hello, world!"
    assert messages[1].content == "Hi! How are you?"
    assert len(other_messages) == 3
    assert other_messages[0].content == "Olá!"
    assert other_messages[1].content == "Olá! Como vai?"
    assert other_messages[2].content == "Bem, está quente em Recife?"

    # Test property:
    assert message_history.messages == messages
    assert other_message_history.messages == other_messages


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_aget_messages(thread_aaa, thread_bbb):
    thread = await Thread.objects.aget(name="AAA")
    other_thread = await Thread.objects.aget(name="BBB")

    await Message.objects.abulk_create(
        [
            Message(thread=thread, message={"data": {"content": "Hello, world!"}, "type": "human"}),
            Message(thread=thread, message={"data": {"content": "Hi! How are you?"}, "type": "ai"}),
            Message(thread=other_thread, message={"data": {"content": "Olá!"}, "type": "human"}),
            Message(
                thread=other_thread, message={"data": {"content": "Olá! Como vai?"}, "type": "ai"}
            ),
            Message(
                thread=other_thread,
                message={"data": {"content": "Bem, está quente em Recife?"}, "type": "human"},
            ),
        ]
    )

    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    messages = await message_history.aget_messages()
    other_message_history = DjangoChatMessageHistory(thread_id=other_thread.id)
    other_messages = await other_message_history.aget_messages()

    assert len(messages) == 2
    assert messages[0].content == "Hello, world!"
    assert messages[1].content == "Hi! How are you?"
    assert len(other_messages) == 3
    assert other_messages[0].content == "Olá!"
    assert other_messages[1].content == "Olá! Como vai?"
    assert other_messages[2].content == "Bem, está quente em Recife?"


def test_clear(thread_aaa, thread_bbb):
    thread = Thread.objects.get(name="AAA")
    other_thread = Thread.objects.get(name="BBB")

    Message.objects.bulk_create(
        [
            Message(thread=thread, message={"data": {"content": "Hello, world!"}, "type": "human"}),
            Message(thread=thread, message={"data": {"content": "Hi! How are you?"}, "type": "ai"}),
            Message(thread=other_thread, message={"data": {"content": "Olá!"}, "type": "human"}),
            Message(
                thread=other_thread, message={"data": {"content": "Olá! Como vai?"}, "type": "ai"}
            ),
            Message(
                thread=other_thread,
                message={"data": {"content": "Bem, está quente em Recife?"}, "type": "human"},
            ),
        ]
    )

    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    message_history.clear()

    assert thread.messages.count() == 0
    assert other_thread.messages.count() == 3


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_aclear(thread_aaa, thread_bbb):
    thread = await Thread.objects.aget(name="AAA")
    other_thread = await Thread.objects.aget(name="BBB")

    await Message.objects.abulk_create(
        [
            Message(thread=thread, message={"data": {"content": "Hello, world!"}, "type": "human"}),
            Message(thread=thread, message={"data": {"content": "Hi! How are you?"}, "type": "ai"}),
            Message(thread=other_thread, message={"data": {"content": "Olá!"}, "type": "human"}),
            Message(
                thread=other_thread, message={"data": {"content": "Olá! Como vai?"}, "type": "ai"}
            ),
            Message(
                thread=other_thread,
                message={"data": {"content": "Bem, está quente em Recife?"}, "type": "human"},
            ),
        ]
    )

    message_history = DjangoChatMessageHistory(thread_id=thread.id)
    await message_history.aclear()

    assert await thread.messages.acount() == 0
    assert await other_thread.messages.acount() == 3
