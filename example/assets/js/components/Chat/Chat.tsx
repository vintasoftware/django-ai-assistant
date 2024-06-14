import {
  ActionIcon,
  Avatar,
  Box,
  Button,
  Container,
  Group,
  LoadingOverlay,
  Paper,
  ScrollArea,
  Stack,
  Text,
  Textarea,
  Title,
  Tooltip,
} from "@mantine/core";
import { ThreadsNav } from "../ThreadsNav/ThreadsNav";

import classes from "./Chat.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { IconSend2, IconTrash } from "@tabler/icons-react";
import { getHotkeyHandler } from "@mantine/hooks";
import Markdown from "react-markdown";

import {
  ThreadMessagesSchemaOut,
  ThreadSchema,
  useAssistant,
  useMessage,
  useThread,
} from "django-ai-assistant-client";

function ChatMessage({
  threadId,
  message,
  deleteMessage,
}: {
  threadId: string;
  message: ThreadMessagesSchemaOut;
  deleteMessage: ({
    threadId,
    messageId,
  }: {
    threadId: string;
    messageId: string;
  }) => Promise<void>;
}) {
  const isUserMessage = message.type === "human";

  const DeleteButton = () => (
    <Tooltip label="Delete message" withArrow position="bottom">
      <ActionIcon
        variant="light"
        color="red"
        size="sm"
        onClick={async () => {
          await deleteMessage({ threadId, messageId: message.id });
        }}
        aria-label="Delete message"
      >
        <IconTrash style={{ width: "70%", height: "70%" }} stroke={1.5} />
      </ActionIcon>
    </Tooltip>
  );

  return (
    <Group
      gap="lg"
      align="flex-end"
      justify={isUserMessage ? "flex-end" : "flex-start"}
    >
      {!isUserMessage ? (
        <Avatar color="green" radius="xl">
          AI
        </Avatar>
      ) : null}

      {isUserMessage ? <DeleteButton /> : null}

      <Paper
        flex={1}
        maw="75%"
        shadow="none"
        radius="lg"
        p="xs"
        px="md"
        bg="var(--mantine-color-gray-0)"
      >
        <Group gap="md" justify="space-between" align="top">
          <Markdown className={classes.mdMessage}>{message.content}</Markdown>
        </Group>
      </Paper>

      {!isUserMessage ? <DeleteButton /> : null}
    </Group>
  );
}

function ChatMessageList({
  threadId,
  messages,
  deleteMessage,
}: {
  threadId: string;
  messages: ThreadMessagesSchemaOut[];
  deleteMessage: ({
    threadId,
    messageId,
  }: {
    threadId: string;
    messageId: string;
  }) => Promise<void>;
}) {
  if (messages.length === 0) {
    return <Text c="dimmed">No messages.</Text>;
  }

  return (
    <Stack gap="xl">
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          threadId={threadId}
          message={message}
          deleteMessage={deleteMessage}
        />
      ))}
    </Stack>
  );
}

export function Chat({ assistantId }: { assistantId: string }) {
  const [activeThread, setActiveThread] = useState<ThreadSchema | null>(null);
  const [inputValue, setInputValue] = useState<string>("");

  const { fetchThreads, threads, createThread, deleteThread } = useThread();
  const {
    fetchMessages,
    messages,
    loadingFetchMessages,
    createMessage,
    loadingCreateMessage,
    deleteMessage,
    loadingDeleteMessage,
  } = useMessage();

  const loadingMessages =
    loadingFetchMessages || loadingCreateMessage || loadingDeleteMessage;
  const isThreadSelected = Boolean(activeThread);
  const isChatActive = activeThread && !loadingMessages;

  const scrollViewport = useRef<HTMLDivElement>(null);
  const scrollToBottom = useCallback(
    () =>
      // setTimeout is used because scrollViewport.current?.scrollHeight update is not
      // being triggered in time for the scrollTo method to work properly.
      setTimeout(
        () =>
          scrollViewport.current?.scrollTo({
            top: scrollViewport.current!.scrollHeight,
            behavior: "smooth",
          }),
        500
      ),
    [scrollViewport]
  );

  // Load threads when component mounts:
  useEffect(() => {
    fetchThreads();
  }, [fetchThreads]);

  // Load messages when threadId changes:
  useEffect(() => {
    if (!assistantId) return;
    if (!activeThread) return;

    fetchMessages({
      threadId: activeThread.id,
    });
    scrollToBottom();
  }, [assistantId, activeThread?.id, fetchMessages]);

  async function handleCreateMessage() {
    if (!activeThread) return;

    await createMessage({
      threadId: activeThread.id,
      assistantId,
      messageTextValue: inputValue,
    });

    setInputValue("");
    scrollToBottom();
  }

  return (
    <>
      <ThreadsNav
        threads={threads}
        selectedThreadId={activeThread?.id}
        selectThread={setActiveThread}
        createThread={createThread}
        deleteThread={deleteThread}
      />
      <main className={classes.main}>
        <Container className={classes.chatContainer}>
          <Stack className={classes.chat}>
            <Title mt="md" order={2}>
              Chat: {assistantId}
            </Title>
            <ScrollArea
              pos="relative"
              type="auto"
              h="100%"
              px="xs"
              viewportRef={scrollViewport}
            >
              <LoadingOverlay
                visible={loadingMessages}
                zIndex={1000}
                overlayProps={{ blur: 2 }}
              />
              {isThreadSelected ? (
                <ChatMessageList
                  threadId={activeThread.id}
                  messages={messages || []}
                  deleteMessage={deleteMessage}
                />
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
