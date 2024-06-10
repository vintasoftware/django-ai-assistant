import { useCallback } from "react";
import { useState } from "react";
import {
  ThreadMessagesSchemaOut,
  djangoAiAssistantViewsCreateThreadMessage,
  djangoAiAssistantViewsListThreadMessages,
} from "../client";
import { Callbacks } from "./types";

/**
 * React hook to manage the Message resource.
 */
export function useMessage() {
  const [messages, setMessages] = useState<ThreadMessagesSchemaOut[]>([]);
  const [loadingFetch, setLoadingFetch] = useState<boolean>(false);
  const [loadingCreate, setLoadingCreate] = useState<boolean>(false);

  /**
   * Fetches a list of messages.
   *
   * @param threadId The ID of the thread for which to fetch messages.
   * @param onSuccess Callback function called upon successful fetching of messages.
   * @param onError Callback function called upon error while fetching messages.
   */
  const fetchMessages = useCallback(
    async ({
      threadId,
      onSuccess,
      onError,
    }: {
      threadId: string;
    } & Callbacks) => {
      try {
        setLoadingFetch(true);
        const fetchedMessages = await djangoAiAssistantViewsListThreadMessages({
          threadId: threadId,
        });
        setMessages(fetchedMessages);
        onSuccess?.();
      } catch (error) {
        console.error(error);
        onError?.(error);
      } finally {
        setLoadingFetch(false);
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
   * @param onSuccess Callback function called upon successful creation of the message.
   * @param onError Callback function called upon error while creating the message.
   * @returns The created message, or null if creation fails.
   */
  const createMessage = useCallback(
    async ({
      threadId,
      assistantId,
      messageTextValue,
      onSuccess,
      onError,
    }: {
      threadId: string;
      assistantId: string;
      messageTextValue: string;
    } & Callbacks): Promise<ThreadMessagesSchemaOut | null> => {
      try {
        setLoadingCreate(true);
        const message = await djangoAiAssistantViewsCreateThreadMessage({
          threadId,
          requestBody: {
            content: messageTextValue,
            assistant_id: assistantId,
          },
        });
        await fetchMessages({ threadId });
        onSuccess?.();
        // FIXME: The schema is returning unknown, but it should be ThreadMessagesSchemaOut.
        // We should check the backend to fix this.
        return message as ThreadMessagesSchemaOut;
      } catch (error) {
        console.error(error);
        onError?.(error);
        return null;
      } finally {
        setLoadingCreate(false);
      }
    },
    [fetchMessages]
  );

  return {
    /**
     * Function to fetch messages for a thread from the server.
     */
    fetchResource: fetchMessages,
    /**
     * Function to create a new message in a thread.
     */
    createResource: createMessage,
    /**
     * Array of fetched messages.
     */
    resources: messages,
    /**
     * Loading state of the fetch operation.
     */
    loadingFetch,
    /**
     * Loading state of the create operation.
     */
    loadingCreate,
  };
}
