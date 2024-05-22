import {
  Container,
  Text,
  Stack,
  Title,
  TextInput,
  Textarea,
  Group,
  Box,
  Flex,
  ActionIcon,
  Button,
  Code,
  LoadingOverlay,
  ScrollArea,
} from "@mantine/core";
import { ThreadsNav } from "./ThreadsNav";
import OpenAI from "openai";
import cookie from "cookie";

import classes from "./Chat.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { IconSend2 } from "@tabler/icons-react";
import { getHotkeyHandler } from "@mantine/hooks";

function csrfFetch(url: string, options: RequestInit = {}) {
  const { csrftoken } = cookie.parse(document.cookie);

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      "X-CSRFToken": csrftoken,
    },
    credentials: "include",
  });
}

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
  return (
    <div>
      {messages.map((message, index) => (
        <ChatMessage key={index} message={message} />
      ))}
    </div>
  );
}

async function fetchMessages({ threadId }: { threadId: string }) {
  const response = await csrfFetch(
    `/ai-assistant/threads/${threadId}/messages/`
  );
  return response.json();
}

async function createMessage({
  threadId,
  content,
}: {
  threadId: string;
  content: string;
}) {
  await csrfFetch(`/ai-assistant/threads/${threadId}/messages/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }),
  });
}

export function Chat() {
  const threadId = "thread_95qH0BqgjbvBYUTiBttGLEum";

  const [inputValue, setInputValue] = useState<string>("");
  const [messages, setMessages] = useState<OpenAI.Beta.Threads.Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const scrollViewport = useRef<HTMLDivElement>(null);
  const scrollToBottom = useCallback(
    () =>
      scrollViewport.current?.scrollTo({
        top: scrollViewport.current!.scrollHeight,
        behavior: "smooth",
      }),
    [scrollViewport]
  );

  const loadMessages = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetchMessages({ threadId });
      const messages = response.data as OpenAI.Beta.Threads.Message[];
      messages.reverse();
      setMessages(messages);
      scrollToBottom();
    } catch (error) {
      console.error(error);
      alert("Error while loading messages");
    }
    setIsLoading(false);
  }, [threadId]);

  const sendMessage = useCallback(async () => {
    setIsLoading(true);
    try {
      setInputValue("");
      await createMessage({ threadId, content: inputValue });
      await loadMessages();
    } catch (error) {
      console.error(error);
      alert("Error while sending message");
    }
    setIsLoading(false);
  }, [threadId, inputValue]);

  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  return (
    <>
      <ThreadsNav />
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
              <ChatMessageList messages={messages} />
            </ScrollArea>
            <Textarea
              mt="auto"
              mb="3rem"
              placeholder="Enter user message… (Ctrl↵ to send)"
              autosize
              minRows={2}
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
                  onClick={sendMessage}
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
