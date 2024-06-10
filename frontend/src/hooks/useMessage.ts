import { useCallback } from "react";
import { useState } from "react";
import {
  ThreadMessagesSchemaOut,
  djangoAiAssistantViewsCreateThreadMessage,
  djangoAiAssistantViewsListThreadMessages,
} from "../client";

/**
 * React hook to manage the Message resource.
 */
export function useMessage() {
  const [messages, setMessages] = useState<ThreadMessagesSchemaOut[]>([]);
  const [loadingFetchMessages, setLoadingFetchMessages] =
    useState<boolean>(false);
  const [loadingCreateMessage, setLoadingCreateMessage] =
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
   * @returns A promise that resolves with the created message.
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
    }): Promise<ThreadMessagesSchemaOut> => {
      try {
        setLoadingCreateMessage(true);
        const message = await djangoAiAssistantViewsCreateThreadMessage({
          threadId,
          requestBody: {
            content: messageTextValue,
            assistant_id: assistantId,
          },
        });
        await fetchMessages({ threadId });
        // FIXME: The schema is returning unknown, but it should be ThreadMessagesSchemaOut.
        // We should check the backend to fix this.
        return message as ThreadMessagesSchemaOut;
      } finally {
        setLoadingCreateMessage(false);
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
  };
}
