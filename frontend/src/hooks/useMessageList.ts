import { useCallback } from "react";
import { useState } from "react";
import {
  aiCreateThreadMessage,
  aiDeleteThreadMessage,
  aiListThreadMessages,
  ThreadMessage,
} from "../client";

function hasNullThreadId(
  threadId: string | null,
  operation: string | null = "fetch"
): threadId is null {
  if (threadId == null) {
    console.warn(
      `threadId is null or undefined. Ignoring ${operation} operation.`
    );
    return true;
  }
  return false;
}

/**
 * React hook to manage the list, create, and delete of Messages.
 *
 * @param threadId The ID of the thread for which to manage messages.
 */
export function useMessageList({ threadId }: { threadId: string | null }) {
  const [messages, setMessages] = useState<ThreadMessage[] | null>(
    null
  );
  const [loadingFetchMessages, setLoadingFetchMessages] =
    useState<boolean>(false);
  const [loadingCreateMessage, setLoadingCreateMessage] =
    useState<boolean>(false);
  const [loadingDeleteMessage, setLoadingDeleteMessage] =
    useState<boolean>(false);

  /**
   * Fetches a list of messages.
   * Does nothing if `threadId` of `useMessageList` hook is null.
   *
   * @returns - A promise that resolves with the fetched list of messages.
   */
  const fetchMessages = useCallback(async (): Promise<
    ThreadMessage[] | null
  > => {
    if (hasNullThreadId(threadId)) return null;

    try {
      setLoadingFetchMessages(true);
      const fetchedMessages = await aiListThreadMessages({
        threadId: threadId,
      });
      setMessages(fetchedMessages);
      return fetchedMessages;
    } finally {
      setLoadingFetchMessages(false);
    }
  }, [threadId]);

  /**
   * Creates a new message in a thread.
   * Does nothing if `threadId` of `useMessageList` hook is null.
   *
   * @param assistantId The ID of the assistant.
   * @param messageTextValue The content of the message.
   */
  const createMessage = useCallback(
    async ({
      assistantId,
      messageTextValue,
    }: {
      assistantId: string;
      messageTextValue: string;
    }): Promise<void> => {
      if (hasNullThreadId(threadId, "create")) return;

      try {
        setLoadingCreateMessage(true);
        // successful response is 201, None
        await aiCreateThreadMessage({
          threadId,
          requestBody: {
            content: messageTextValue,
            assistant_id: assistantId,
          },
        });
        await fetchMessages();
      } finally {
        setLoadingCreateMessage(false);
      }
    },
    [fetchMessages, threadId]
  );

  /**
   * Deletes a message in a thread.
   * Does nothing if `threadId` of `useMessageList` hook is null.
   *
   * @param threadId The ID of the thread in which to delete the message.
   * @param messageId The ID of the message to delete.
   */
  const deleteMessage = useCallback(
    async ({ messageId }: { messageId: string }): Promise<void> => {
      if (hasNullThreadId(threadId, "delete")) return;

      try {
        setLoadingDeleteMessage(true);
        await aiDeleteThreadMessage({
          threadId,
          messageId,
        });
        await fetchMessages();
      } finally {
        setLoadingDeleteMessage(false);
      }
    },
    [fetchMessages, threadId]
  );

  return {
    /**
     * Function to fetch messages for a thread from the server.
     */
    fetchMessages,
    /**
     * Function to create a new message in a thread.
     */
    createMessage,
    /**
     * Function to delete a message in a thread.
     */
    deleteMessage,
    /**
     * Array of fetched messages.
     */
    messages,
    /**
     * Loading state of the fetch operation.
     */
    loadingFetchMessages,
    /**
     * Loading state of the create operation.
     */
    loadingCreateMessage,
    /**
     * Loading state of the delete operation.
     */
    loadingDeleteMessage,
  };
}
