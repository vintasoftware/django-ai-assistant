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
  Card,
  Image,
  Group,
  Flex,
} from "@mantine/core";
import { ThreadsNav } from "./ThreadsNav";

import classes from "./Chat.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { IconSend2 } from "@tabler/icons-react";
import { getHotkeyHandler } from "@mantine/hooks";
import Markdown from "react-markdown";
import {
  DjangoMessage,
  DjangoThread,
  createMessage,
  createThread,
  fetchAssistantID,
  fetchDjangoThreads,
  fetchMessages,
} from "@/api";

interface MovieRecommendation {
  movie_name: string;
  movie_description: string;
  movie_poster_image_url: string;
  imdb_url: string;
}

function MovieCard({
  movieRecommendation,
}: {
  movieRecommendation: MovieRecommendation;
}) {
  return (
    <Card
      maw={300}
      mih={400}
      mb="xs"
      shadow="sm"
      padding="lg"
      radius="md"
      withBorder
    >
      <Card.Section>
        <Image src={movieRecommendation.movie_poster_image_url} height={160} />
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

function ChatMessage({ message }: { message: DjangoMessage }) {
  if (message.type === "ai") {
    const movies = JSON.parse(message.content);
    if (movies.recommended_movies.length > 0) {
      const cards = movies.recommended_movies.map(
        (movieRecommendation: MovieRecommendation, index: number) => (
          <MovieCard key={index} movieRecommendation={movieRecommendation} />
        )
      );
      return (
        <Flex
          mih={50}
          gap="sm"
          justify="flex-start"
          align="center"
          direction="row"
          wrap="wrap"
        >
          {cards}
        </Flex>
      );
    }
  }
  return (
    <Box mb="md">
      <Text fw={700}>"User"</Text>
      <Markdown className={classes.mdMessage}>{message.content}</Markdown>
    </Box>
  );
}

function ChatMessageList({ messages }: { messages: DjangoMessage[] }) {
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
  const [messages, setMessages] = useState<DjangoMessage[]>([]);
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
      scrollToBottom(); // TODO: not working?
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
