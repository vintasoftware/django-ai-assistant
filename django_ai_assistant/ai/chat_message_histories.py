"""Client for persisting chat message history in a Django database.
This client provides support for both sync and async.
Note: the Django database must support JSONField.
See: https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield
Based on langchain-postgres
"""
from __future__ import annotations

import logging
from typing import Any, List, Sequence, cast

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from django_ai_assistant.models import Message


logger = logging.getLogger(__name__)


class DjangoChatMessageHistory(BaseChatMessageHistory):
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

        This chat client needs to be used in Django context to interact with the database.

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
        Message.objects.bulk_create(
            [
                Message(thread_id=self._thread_id, message=message_to_dict(message))
                for message in messages
            ]
        )

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add messages to the chat thread.

        Args:
            messages: A list of BaseMessage objects to store.
        """
        await Message.objects.abulk_create(
            [
                Message(thread_id=self._thread_id, message=message_to_dict(message))
                for message in messages
            ]
        )

    def get_messages(self) -> List[BaseMessage]:
        """Retrieve messages from the chat thread."""
        items = cast(
            Sequence[dict],
            Message.objects.filter(thread_id=self._thread_id).values_list("message", flat=True),
        )
        messages = messages_from_dict(items)
        return messages

    async def _async_messages_gen(self):
        async for m in Message.objects.filter(thread_id=self._thread_id).values_list(
            "message", flat=True
        ):
            yield m

    async def aget_messages(self) -> List[BaseMessage]:
        """Retrieve messages from the thread."""
        items = cast(Sequence[dict], self._async_messages_gen())
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
