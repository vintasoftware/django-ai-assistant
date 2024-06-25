"""Client for persisting chat message history in a Django database.
This client provides support for both sync and async.
Note: the Django database must support JSONField.
See: https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield
Based on langchain-postgres
"""
from __future__ import annotations

import logging
from typing import Any, List, Sequence, cast

from django.db import transaction

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from django_ai_assistant.decorators import with_cast_id
from django_ai_assistant.models import Message


logger = logging.getLogger(__name__)


class DjangoChatMessageHistory(BaseChatMessageHistory):
    @with_cast_id
    def __init__(
        self,
        thread_id: Any,
    ) -> None:
        """Client for persisting chat message history in a Django database.

        This client provides support for both sync and async.

        The client provides methods to add messages, get messages,
        and clear the chat message history of a thread.

        The schema has the following columns:

        - id: A serial primary key.
        - thread_id: The thread ID for the chat message history.
        - message: The JSONB message content.
        - created_at: The timestamp of when the message was created.

        Messages are retrieved for a given thread_id and are sorted by
        the order in which the messages were added to the thread.

        The "created_at" column is not returned by the interface, but
        has been added for the schema so the information is available in the database.

        A thread_id can be used to separate different chat histories in the same table,
        the thread_id should be provided when initializing the client.

        This client needs to be used in Django context to interact with the database.

        Args:
            thread_id: The thread ID to use for the chat message history
            sync_connection: An existing psycopg connection instance
            async_connection: An existing psycopg async connection instance

        Usage:
            - Initialize the class with the appropriate thread ID, table name,
              and database connection.
            - Add messages to the database using add_messages or aadd_messages.
            - Retrieve messages with get_messages or aget_messages.
            - Clear the thread with clear or aclear when needed.
        """
        self._thread_id = thread_id

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add messages to the chat thread.

        Args:
            messages: A list of BaseMessage objects to store.
        """
        with transaction.atomic():
            created_messages = Message.objects.bulk_create(
                [Message(thread_id=self._thread_id, message=dict()) for message in messages]
            )

            # Update langchain message IDs with Django message IDs
            for idx, created_message in enumerate(created_messages):
                message_with_id = messages[idx]
                message_with_id.id = str(created_message.id)
                created_message.message = message_to_dict(message_with_id)

            Message.objects.bulk_update(created_messages, ["message"])

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add messages to the chat thread.

        Args:
            messages: A list of BaseMessage objects to store.
        """
        # NOTE: This method does not use transactions because it do not yet work in async mode.
        # Source: https://docs.djangoproject.com/en/5.0/topics/async/#queries-the-orm
        created_messages = await Message.objects.abulk_create(
            [Message(thread_id=self._thread_id, message=dict()) for message in messages]
        )

        # Update langchain message IDs with Django message IDs
        for idx, created_message in enumerate(created_messages):
            message_with_id = messages[idx]
            message_with_id.id = str(created_message.id)
            created_message.message = message_to_dict(message_with_id)

        await Message.objects.abulk_update(created_messages, ["message"])

    @with_cast_id
    def remove_messages(self, message_ids: List[Any]) -> None:
        """Remove messages from the chat thread.

        Args:
            message_ids: A list of message IDs to remove.
        """
        Message.objects.filter(id__in=message_ids).delete()

    @with_cast_id
    async def aremove_messages(self, message_ids: List[Any]) -> None:
        """Remove messages from the chat thread.

        Args:
            message_ids: A list of message IDs to remove.
        """
        await Message.objects.filter(id__in=message_ids).adelete()

    def _get_messages_qs(self):
        return Message.objects.filter(thread_id=self._thread_id).order_by("created_at")

    def get_messages(self) -> List[BaseMessage]:
        """Retrieve messages from the chat thread."""
        items = cast(
            Sequence[dict],
            self._get_messages_qs().values_list("message", flat=True),
        )
        messages = messages_from_dict(items)
        return messages

    async def aget_messages(self) -> List[BaseMessage]:
        """Retrieve messages from the thread."""
        items = []
        async for m in self._get_messages_qs().values_list("message", flat=True):
            items.append(m)

        items = cast(Sequence[dict], items)
        messages = messages_from_dict(items)
        return messages

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from the thread."""
        return self.get_messages()

    def clear(self) -> None:
        """Clear the chat message history for the thread."""
        Message.objects.filter(thread_id=self._thread_id).delete()

    async def aclear(self) -> None:
        """Clear the chat message history for the GIVEN thread."""
        await Message.objects.filter(thread_id=self._thread_id).adelete()
