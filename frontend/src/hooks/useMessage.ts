import { useCallback } from "react";
import { useState } from "react";
import {
  djangoAiAssistantViewsCreateThreadMessage,
  djangoAiAssistantViewsDeleteThreadMessage,
  djangoAiAssistantViewsListThreadMessages,
  ThreadMessagesSchemaOut,
} from "../client";

/**
 * React hook to manage the Message resource.
 */
export function useMessage() {
  const [messages, setMessages] = useState<ThreadMessagesSchemaOut[] | null>(
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
   *
   * @param threadId The ID of the thread for which to fetch messages.
   * @returns A promise that resolves with the fetched list of messages.
   */
  const fetchMessages = useCallback(
    async ({
      threadId,
    }: {
      threadId: string;
    }): Promise<ThreadMessagesSchemaOut[]> => {
      try {
        setLoadingFetchMessages(true);
        const fetchedMessages = await djangoAiAssistantViewsListThreadMessages({
          threadId: threadId,
        });
        setMessages(fetchedMessages);
        return fetchedMessages;
      } finally {
        setLoadingFetchMessages(false);
      }
    },
    []
  );

  /**
   * Creates a new message in a thread.
   *
   * @param threadId The ID of the thread in which to create the message.
   * @param assistantId The ID of the assistant.
   * @param messageTextValue The content of the message.
   */
  const createMessage = useCallback(
    async ({
      threadId,
      assistantId,
      messageTextValue,
    }: {
      threadId: string;
      assistantId: string;
      messageTextValue: string;
    }): Promise<void> => {
      try {
        setLoadingCreateMessage(true);
        // successful response is 201, None
        await djangoAiAssistantViewsCreateThreadMessage({
          threadId,
          requestBody: {
            content: messageTextValue,
            assistant_id: assistantId,
          },
        });
        await fetchMessages({ threadId });
      } finally {
        setLoadingCreateMessage(false);
      }
    },
    [fetchMessages]
  );

  /**
   * Deletes a message in a thread.
   *
   * @param threadId The ID of the thread in which to delete the message.
   * @param messageId The ID of the message to delete.
   */
  const deleteMessage = useCallback(
    async ({
      threadId,
      messageId,
    }: {
      threadId: string;
      messageId: string;
    }): Promise<void> => {
      try {
        setLoadingDeleteMessage(true);
        await djangoAiAssistantViewsDeleteThreadMessage({
          threadId,
          messageId,
        });
        await fetchMessages({ threadId });
      } finally {
        setLoadingDeleteMessage(false);
      }
    },
    [fetchMessages]
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
