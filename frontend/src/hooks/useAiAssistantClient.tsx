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

  const [threads, setThreads] = useState<ThreadSchema[] | null>(null);
  const [activeThread, setActiveThread] = useState<ThreadSchema | null>(null);

  const [messages, setMessages] = useState<ThreadMessagesSchemaOut[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState<boolean>(false);

  const fetchAssistants = useCallback(async () => {
    try {
      setAssistants(await djangoAiAssistantViewsListAssistants());
    } catch (error) {
      console.error(error);
    }
  }, []);

  const fetchThreads = useCallback(async () => {
    try {
      setThreads(null);
      setThreads(await djangoAiAssistantViewsListThreads());
    } catch (error) {
      console.error(error);
    }
  }, []);

  const createAndSetActiveThread = useCallback(async () => {
    try {
      await fetchThreads();
      setActiveThread(
        await djangoAiAssistantViewsCreateThread({
          requestBody: {
            name: undefined,
          },
        })
      );
    } catch (error) {
      console.error(error);
      // alert("Error while creating thread");
    }
  }, []);

  const fetchMessages = useCallback(
    async ({
      successCallback,
    }: { successCallback?: CallableFunction } = {}) => {
      setIsLoadingMessages(true);
      try {
        setMessages(
          await djangoAiAssistantViewsListThreadMessages({
            threadId: activeThread?.id,
          })
        );
        successCallback?.();
      } catch (error) {
        console.error(error);
        // alert("Error while loading messages");
      }
      setIsLoadingMessages(false);
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
      setIsLoadingMessages(true);
      try {
        await djangoAiAssistantViewsCreateThreadMessage({
          threadId: activeThread?.id,
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
      setIsLoadingMessages(false);
    },
    [activeThread?.id]
  );

  return {
    assistants,
    fetchAssistants,

    threads,
    fetchThreads,
    createThread: createAndSetActiveThread,
    activeThread,
    setActiveThread,

    messages,
    fetchMessages,
    isLoadingMessages,
    createMessage,
  };
}
