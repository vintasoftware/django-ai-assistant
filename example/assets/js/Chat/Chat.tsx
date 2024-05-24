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
import OpenAI from "openai";

import classes from "./Chat.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { IconSend2 } from "@tabler/icons-react";
import { getHotkeyHandler } from "@mantine/hooks";
import {
  DjangoThread,
  createMessage,
  createThread,
  fetchAssistantID,
  fetchDjangoThreads,
  fetchMessages,
} from "@/api";

function ChatMessage({ message }: { message: OpenAI.Beta.Threads.Message }) {
  return (
    <Box mb="md">
      <Text fw={700} style={{ textTransform: "capitalize" }}>
        {message.role}
      </Text>
      {message.content.map((content, index) => {
        let text;
        if (content.type !== "text") {
          text = "Unsupported content type: {content.type}";
        } else {
          text = content.text.value;
        }
        return <Text key={index}>{text}</Text>;
      })}
    </Box>
  );
}

function ChatMessageList({
  messages,
}: {
  messages: OpenAI.Beta.Threads.Message[];
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
  const [threads, setThreads] = useState<DjangoThread[] | null>(null);
  const [threadId, setThreadId] = useState<string>("");
  const [inputValue, setInputValue] = useState<string>("");
  const [messages, setMessages] = useState<OpenAI.Beta.Threads.Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const isThreadSelected = assistantId && threadId;
  const isChatActive = assistantId && threadId && !isLoading;

  const scrollViewport = useRef<HTMLDivElement>(null);
  const scrollToBottom = useCallback(
    () =>
      scrollViewport.current?.scrollTo({
        top: scrollViewport.current!.scrollHeight,
        behavior: "smooth",
      }),
    [scrollViewport]
  );

  const loadThreads = useCallback(async () => {
    try {
      setThreads(null);
      const threads = await fetchDjangoThreads();
      setThreads(threads);
    } catch (error) {
      console.error(error);
      // alert("Error while loading threads");
    }
  }, []);

  const createAndSetThread = useCallback(async () => {
    try {
      const thread = await createThread();
      await loadThreads();
      setThreadId(thread.id);
    } catch (error) {
      console.error(error);
      // alert("Error while creating thread");
    }
  }, []);

  const loadMessages = useCallback(async () => {
    setIsLoading(true);
    try {
      console.log(threadId);
      setMessages(await fetchMessages({ threadId }));
      scrollToBottom();
    } catch (error) {
      console.error(error);
      // alert("Error while loading messages");
    }
    setIsLoading(false);
  }, [threadId]);

  const sendMessage = useCallback(async () => {
    setIsLoading(true);
    try {
      setInputValue("");
      await createMessage({ threadId, assistantId, content: inputValue });
      await loadMessages();
    } catch (error) {
      console.error(error);
      // alert("Error while sending message");
    }
    setIsLoading(false);
  }, [threadId, inputValue]);

  // Load assistantId when component mounts:
  useEffect(() => {
    async function init() {
      try {
        setAssistantId(await fetchAssistantID());
      } catch (error) {
        console.error(error);
        // alert("Error while fetching assistant");
      }
    }
    init();
  }, []);

  // Load threads when component mounts:
  useEffect(() => {
    loadThreads();
  }, [loadThreads]);

  // Load messages when threadId changes:
  useEffect(() => {
    if (!assistantId) return;
    if (!threadId) return;
    loadMessages();
  }, [loadMessages]);

  return (
    <>
      <ThreadsNav
        threads={threads}
        selectedThreadId={threadId}
        selectThread={setThreadId}
        createThread={createAndSetThread}
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
                visible={isLoading}
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
              onKeyDown={getHotkeyHandler([["mod+Enter", sendMessage]])}
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
                    sendMessage();
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
