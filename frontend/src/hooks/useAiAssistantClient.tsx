import { useCallback } from "react";
import { useState } from "react";
import {
  AssistantSchema,
  ThreadMessagesSchemaOut,
  ThreadSchema,
  djangoAiAssistantViewsCreateThread,
  djangoAiAssistantViewsCreateThreadMessage,
  djangoAiAssistantViewsListAssistants,
  djangoAiAssistantViewsListThreadMessages,
  djangoAiAssistantViewsListThreads,
} from "../client";

/**
 * React hook to use the AI Assistant client.
 * @returns Object with AI Assistant client methods and data.
 */
export function useAiAssistantClient() {
  const [assistants, setAssistants] = useState<AssistantSchema[] | null>(null);
  const [loadingFetchAssistants, setLoadingFetchAssistants] =
    useState<boolean>(false);

  const [threads, setThreads] = useState<ThreadSchema[] | null>(null);
  const [activeThread, setActiveThread] = useState<ThreadSchema | null>(null);
  const [loadingFetchThreads, setLoadingFetchThreads] =
    useState<boolean>(false);
  const [loadingCreateThread, setLoadingCreateThread] =
    useState<boolean>(false);

  const [messages, setMessages] = useState<ThreadMessagesSchemaOut[]>([]);
  const [loadingFetchMessages, setLoadingFetchMessages] =
    useState<boolean>(false);
  const [loadingCreateMessage, setLoadingCreateMessage] =
    useState<boolean>(false);

  const fetchAssistants = useCallback(async () => {
    try {
      setLoadingFetchAssistants(true);

      setAssistants(await djangoAiAssistantViewsListAssistants());

      setLoadingFetchAssistants(false);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const fetchThreads = useCallback(async () => {
    try {
      setLoadingFetchThreads(true);

      setThreads(null);
      setThreads(await djangoAiAssistantViewsListThreads());

      setLoadingFetchThreads(false);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const createThread = useCallback(async () => {
    try {
      setLoadingCreateThread(true);

      setActiveThread(
        await djangoAiAssistantViewsCreateThread({
          requestBody: {
            name: undefined,
          },
        })
      );
      await fetchThreads();

      setLoadingCreateThread(false);
    } catch (error) {
      console.error(error);
      // alert("Error while creating thread");
    }
  }, [fetchThreads]);

  const fetchMessages = useCallback(
    async ({
      successCallback,
    }: { successCallback?: CallableFunction } = {}) => {
      if (!activeThread?.id) return;

      setLoadingFetchMessages(true);

      try {
        setMessages(
          await djangoAiAssistantViewsListThreadMessages({
            threadId: activeThread?.id.toString(),
          })
        );
        successCallback?.();
      } catch (error) {
        console.error(error);
        // alert("Error while loading messages");
      }

      setLoadingFetchMessages(false);
    },
    [activeThread?.id]
  );

  const createMessage = useCallback(
    async ({
      assistantId,
      messageTextValue,
      successCallback,
    }: {
      assistantId: string;
      messageTextValue: string;
      successCallback?: CallableFunction;
    }) => {
      if (!activeThread?.id) return;

      setLoadingCreateMessage(true);

      try {
        await djangoAiAssistantViewsCreateThreadMessage({
          threadId: activeThread?.id?.toString(),
          requestBody: {
            content: messageTextValue,
            assistant_id: assistantId,
          },
        });
        await fetchMessages();
        successCallback?.();
      } catch (error) {
        console.error(error);
        // alert("Error while sending message");
      }

      setLoadingCreateMessage(false);
    },
    [fetchMessages, activeThread?.id]
  );

  return {
    assistants,
    fetchAssistants,
    loadingFetchAssistants,

    threads,
    fetchThreads,
    loadingFetchThreads,
    createThread,
    loadingCreateThread,
    activeThread,
    setActiveThread,

    messages,
    fetchMessages,
    loadingFetchMessages,
    createMessage,
    loadingCreateMessage,
  };
}
