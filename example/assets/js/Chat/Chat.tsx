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
} from "@mantine/core";
import { ThreadsNav } from "./ThreadsNav";
import OpenAI from "openai";

import classes from "./Chat.module.css";
import { useEffect, useState } from "react";

function ChatMessage({ message }: { message: OpenAI.Beta.Threads.Message }) {
  return (
    <Box className={classes.chatMessage} mb="md">
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
        return (
          <Text key={index} mt="sm">
            {text}
          </Text>
        );
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

async function getMessages({ threadId }: { threadId: string }) {
  const response = await fetch(`/ai-assistant/threads/${threadId}/messages`);
  return response.json();
}

export function Chat() {
  const threadId = "thread_s5Dxm6QTPhjOhA0ZFqZ6HXf2";

  const [messages, setMessages] = useState<OpenAI.Beta.Threads.Message[]>([]);

  useEffect(() => {
    getMessages({ threadId }).then((response) => {
      const messages = response.data as OpenAI.Beta.Threads.Message[];
      messages.reverse();
      setMessages(messages);
    });
  });

  return (
    <>
      <ThreadsNav />
      <main className={classes.main}>
        <Container className={classes.chatContainer}>
          <Stack className={classes.chat}>
            <Title mt="md" order={2}>
              Chat
            </Title>
            <Stack className={classes.chatMessages}>
              <ChatMessageList messages={messages} />
            </Stack>
            <Textarea mt="auto" mb="3rem" placeholder="Enter user message…" />
          </Stack>
        </Container>
      </main>
    </>
  );
}
