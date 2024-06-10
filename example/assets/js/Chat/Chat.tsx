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

import {
  ThreadMessagesSchemaOut,
  ThreadSchema,
  useAssistant,
  useMessage,
  useThread,
} from "django-ai-assistant-client";

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

export function Chat() {
  const [assistantId, setAssistantId] = useState<string>("");
  const [activeThread, setActiveThread] = useState<ThreadSchema | null>(null);
  const [inputValue, setInputValue] = useState<string>("");

  const { fetchAssistants, assistants } = useAssistant();
  const { fetchThreads, threads, createThread } = useThread();
  const {
    fetchMessages,
    messages,
    loadingFetchMessages,
    createMessage,
    loadingCreateMessage,
  } = useMessage();

  const loadingMessages = loadingFetchMessages || loadingCreateMessage;
  const isThreadSelected = assistantId && activeThread;
  const isChatActive = assistantId && activeThread && !loadingMessages;

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
                visible={loadingMessages}
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
