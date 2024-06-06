import {
  Container,
  Text,
  Stack,
  Title,
  Textarea,
  Box,
  Button,
  LoadingOverlay,
  ScrollArea,
} from "@mantine/core";
import { ThreadsNav } from "./ThreadsNav";

import classes from "./Chat.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { IconSend2 } from "@tabler/icons-react";
import { getHotkeyHandler } from "@mantine/hooks";
import * as client from "@/client";
import type {
  AssistantSchema,
  ThreadMessagesSchemaOut,
  ThreadSchema,
} from "@/client";

function ChatMessage({ message }: { message: ThreadMessagesSchemaOut }) {
  return (
    <Box mb="md">
      <Text fw={700}>{message.type === "ai" ? "AI" : "User"}</Text>
      <Text>{message.content}</Text>
    </Box>
  );
}

function ChatMessageList({
  messages,
}: {
  messages: ThreadMessagesSchemaOut[];
}) {
  if (messages.length === 0) {
    return <Text c="dimmed">No messages.</Text>;
  }

  // TODO: check why horizontal scroll appears
  return (
    <div>
      {messages.map((message, index) => (
        <ChatMessage key={index} message={message} />
      ))}
    </div>
  );
}

function useAiAssistantClient(client: any) {
  // TODO:
  // 1. Move to frontend/src/hooks/useAiAssistantClient.tsx
  // 2. Add loading for each request
  // 3. Improve return of fetch functions

  const [assistants, setAssistants] = useState<AssistantSchema[] | null>(null);

  const [threads, setThreads] = useState<ThreadSchema[] | null>(null);
  const [activeThread, setActiveThread] = useState<ThreadSchema | null>(null);

  const [messages, setMessages] = useState<ThreadMessagesSchemaOut[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState<boolean>(false);

  const fetchAssistants = useCallback(async () => {
    try {
      setAssistants(await client.djangoAiAssistantViewsListAssistants());
    } catch (error) {
      console.error(error);
    }
  }, []);

  const fetchThreads = useCallback(async () => {
    try {
      setThreads(null);
      setThreads(await client.djangoAiAssistantViewsListThreads());
    } catch (error) {
      console.error(error);
    }
  }, []);

  const createAndSetActiveThread = useCallback(async () => {
    try {
      await fetchThreads();
      setActiveThread(
        await client.djangoAiAssistantViewsCreateThread({
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
          await client.djangoAiAssistantViewsListThreadMessages({
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
        await client.djangoAiAssistantViewsCreateThreadMessage({
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

export function Chat() {
  const [assistantId, setAssistantId] = useState<string>("");
  const [inputValue, setInputValue] = useState<string>("");

  const {
    assistants,
    fetchAssistants,
    threads,
    fetchThreads,
    createThread,
    activeThread,
    setActiveThread,
    messages,
    fetchMessages,
    isLoadingMessages,
    createMessage,
  } = useAiAssistantClient(client);

  const isThreadSelected = assistantId && activeThread;
  const isChatActive = assistantId && activeThread && !isLoadingMessages;

  const scrollViewport = useRef<HTMLDivElement>(null);
  const scrollToBottom = useCallback(
    () =>
      scrollViewport.current?.scrollTo({
        top: scrollViewport.current!.scrollHeight,
        behavior: "smooth",
      }),
    [scrollViewport]
  );

  // Load assistantId when component mounts:
  useEffect(() => {
    if (assistants) {
      setAssistantId(assistants[0].id);
    } else {
      fetchAssistants();
    }
  }, [assistants, fetchAssistants]);

  // Load threads when component mounts:
  useEffect(() => {
    fetchThreads();
  }, [fetchThreads]);

  // Load messages when threadId changes:
  useEffect(() => {
    if (!assistantId) return;
    if (!activeThread) return;

    fetchMessages({ successCallback: scrollToBottom });
  }, [assistantId, activeThread?.id, fetchMessages, scrollToBottom]);

  function handleCreateMessage() {
    createMessage({
      assistantId,
      messageTextValue: inputValue,
      successCallback: () => {
        setInputValue("");
        scrollToBottom();
      },
    });
  }

  return (
    <>
      <ThreadsNav
        threads={threads}
        selectedThreadId={activeThread?.id}
        selectThread={setActiveThread}
        createThread={createThread}
      />
      <main className={classes.main}>
        <Container className={classes.chatContainer}>
          <Stack className={classes.chat}>
            <Title mt="md" order={2}>
              Chat
            </Title>
            <ScrollArea
              pos="relative"
              type="auto"
              h="100%"
              px="xs"
              viewportRef={scrollViewport}
            >
              <LoadingOverlay
                visible={isLoadingMessages}
                zIndex={1000}
                overlayProps={{ blur: 2 }}
              />
              {isThreadSelected ? (
                <ChatMessageList messages={messages} />
              ) : (
                <Text c="dimmed">
                  Select or create a thread to start chatting.
                </Text>
              )}
            </ScrollArea>
            <Textarea
              mt="auto"
              mb="3rem"
              placeholder={
                isChatActive
                  ? "Enter user message… (Ctrl↵ to send)"
                  : "Please create or select a thread on the sidebar"
              }
              autosize
              minRows={2}
              disabled={!isChatActive}
              onChange={(e) => setInputValue(e.currentTarget.value)}
              value={inputValue}
              onKeyDown={getHotkeyHandler([["mod+Enter", handleCreateMessage]])}
              rightSection={
                <Button
                  variant="filled"
                  color="teal"
                  aria-label="Send message"
                  fz="xs"
                  rightSection={
                    <IconSend2
                      stroke={1.5}
                      style={{ width: "70%", height: "70%" }}
                    />
                  }
                  disabled={!isChatActive}
                  onClick={(e) => {
                    handleCreateMessage();
                    e.preventDefault();
                  }}
                >
                  Send
                </Button>
              }
              rightSectionWidth={120}
            />
          </Stack>
        </Container>
      </main>
    </>
  );
}
