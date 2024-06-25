import {
  ActionIcon,
  Avatar,
  Badge,
  Box,
  Button,
  Card,
  Container,
  Group,
  Image,
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
  useMessageList,
  useThreadList,
} from "django-ai-assistant-client";


interface MovieRecommendation {
  movie_name: string;
  movie_description: string;
  imdb_movie_poster: string;
  imdb_url: string;
}

function MovieCard(movieRecommendation: MovieRecommendation) {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Card.Section>
        <Image src={movieRecommendation.imdb_movie_poster} height={200} />
      </Card.Section>

      <Group justify="space-between" mt="md" mb="xs">
        <Text fw={500}>{movieRecommendation.movie_name}</Text>
      </Group>

      <Text size="sm" c="dimmed">
        {movieRecommendation.movie_description}
      </Text>

      <Button
        component="a"
        href={movieRecommendation.imdb_url}
        color="blue"
        fullWidth
        mt="md"
        radius="md"
      >
        Visit IMDB
      </Button>
    </Card>
  );
}

function ChatMessage({
  message,
  deleteMessage,
}: {
  message: ThreadMessagesSchemaOut;
  deleteMessage: ({ messageId }: { messageId: string }) => Promise<void>;
}) {
  const isUserMessage = message.type === "human";

  const DeleteButton = () => (
    <Tooltip label="Delete message" withArrow position="bottom">
      <ActionIcon
        variant="light"
        color="red"
        size="sm"
        onClick={async () => {
          await deleteMessage({ messageId: message.id });
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
  messages,
  deleteMessage,
}: {
  messages: ThreadMessagesSchemaOut[];
  deleteMessage: ({ messageId }: { messageId: string }) => Promise<void>;
}) {
  if (messages.length === 0) {
    return <Text c="dimmed">No messages.</Text>;
  }

  return (
    <Stack gap="xl">
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
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

  const { fetchThreads, threads, createThread, deleteThread } = useThreadList();
  const {
    fetchMessages,
    messages,
    loadingFetchMessages,
    createMessage,
    loadingCreateMessage,
    deleteMessage,
    loadingDeleteMessage,
  } = useMessageList({ threadId: activeThread?.id });

  const { fetchAssistant, assistant } = useAssistant({ assistantId });

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

  // Load threads and assistant details when component mounts:
  useEffect(() => {
    fetchThreads();
    fetchAssistant();
  }, [fetchThreads, fetchAssistant]);

  // Load messages when threadId changes:
  useEffect(() => {
    if (!assistantId) return;
    if (!activeThread) return;

    fetchMessages();
    scrollToBottom();
  }, [assistantId, activeThread?.id, fetchMessages]);

  async function handleCreateMessage() {
    if (!activeThread) return;

    await createMessage({
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
              Chat: {assistant?.name || "Loading…"}
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
