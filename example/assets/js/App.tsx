import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import React, { useEffect, useState } from "react";
import {
  Container,
  createTheme,
  List,
  MantineProvider,
  rem,
  ThemeIcon,
  Title,
} from "@mantine/core";
import { Notifications, notifications } from "@mantine/notifications";
import {
  IconBrandDjango,
  IconCloud,
  IconXboxX,
  IconMovie,
  IconChecklist,
  IconPlane,
} from "@tabler/icons-react";
import { Chat, TourGuide } from "@/components";
import { createBrowserRouter, Link, RouterProvider } from "react-router-dom";
import {
  ApiError,
  configAIAssistant,
  useAssistantList,
} from "django-ai-assistant-client";

const theme = createTheme({});

// Relates to path("ai-assistant/", include("django_ai_assistant.urls"))
// which can be found at example/demo/urls.py)
configAIAssistant({ BASE: "ai-assistant" });

const PageWrapper = ({ children }: { children: React.ReactNode }) => {
  // This component allows to use react-router-dom's Link component
  // in the children components.
  return (
    <>
      <Notifications position="top-right" />
      {children}
    </>
  );
};

const ExampleIndex = () => {
  const [showLoginNotification, setShowLoginNotification] =
    useState<boolean>(false);

  const { fetchAssistants } = useAssistantList();

  useEffect(() => {
    // NOTE: In a real application, you should use a more robust
    // authentication check strategy than this.
    async function checkUserIsAuthenticated() {
      try {
        await fetchAssistants();
      } catch (error: ApiError) {
        if (error.status === 401) {
          setShowLoginNotification(true);
        }
      }
    }

    checkUserIsAuthenticated();
  }, [fetchAssistants, setShowLoginNotification]);

  useEffect(() => {
    if (!showLoginNotification) return;

    notifications.show({
      title: "Login Required",
      message: (
        <>
          You must be logged in to engage with the examples. Please{" "}
          <Link to="/admin/" target="_blank">
            log in
          </Link>{" "}
          to continue.
        </>
      ),
      color: "red",
      autoClose: 5000,
      withCloseButton: true,
    });
  }, [showLoginNotification]);

  return (
    <Container>
      <Title order={1} my="md">
        Examples
      </Title>

      <List spacing="sm" size="md" center>
        <List.Item
          icon={
            <ThemeIcon color="blue" size={28} radius="xl">
              <IconCloud style={{ width: rem(18), height: rem(18) }} />
            </ThemeIcon>
          }
        >
          <Link to="/weather-chat">Weather Chat</Link>
        </List.Item>
        <List.Item
          icon={
            <ThemeIcon color="blue" size={28} radius="xl">
              <IconMovie style={{ width: rem(18), height: rem(18) }} />
            </ThemeIcon>
          }
        >
          <Link to="/movies-chat">Movie Recommendation Chat</Link>
        </List.Item>
        <List.Item
          icon={
            <ThemeIcon color="blue" size={28} radius="xl">
              <IconChecklist style={{ width: rem(18), height: rem(18) }} />
            </ThemeIcon>
          }
        >
          <Link to="/issue-tracker-chat">Issue Tracker Chat</Link>
        </List.Item>
        <List.Item
          icon={
            <ThemeIcon color="blue" size={28} radius="xl">
              <IconBrandDjango style={{ width: rem(18), height: rem(18) }} />
            </ThemeIcon>
          }
        >
          <Link to="/rag-chat">Django Docs RAG Chat</Link>
        </List.Item>
        <List.Item
          icon={
            <ThemeIcon color="blue" size={28} radius="xl">
              <IconXboxX style={{ width: rem(18), height: rem(18) }} />
            </ThemeIcon>
          }
        >
          <Link to="/htmx">HTMX demo (no React)</Link>
        </List.Item>
        <List.Item
          icon={
            <ThemeIcon color="blue" size={28} radius="xl">
              <IconPlane style={{ width: rem(18), height: rem(18) }} />
            </ThemeIcon>
          }
        >
          <Link to="/tour-guide">Tour Guide Assistant</Link>
        </List.Item>
      </List>
    </Container>
  );
};

const Redirect = ({ to }: { to: string }) => {
  window.location.href = to;
  return null;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <PageWrapper>
        <ExampleIndex />
      </PageWrapper>
    ),
  },
  {
    path: "/weather-chat",
    element: (
      <PageWrapper>
        <Chat assistantId="weather_assistant" />
      </PageWrapper>
    ),
  },
  {
    path: "/movies-chat",
    element: (
      <PageWrapper>
        <Chat assistantId="movie_recommendation_assistant" />
      </PageWrapper>
    ),
  },
  {
    path: "/issue-tracker-chat",
    element: (
      <PageWrapper>
        <Chat assistantId="issue_tracker_assistant" />
      </PageWrapper>
    ),
  },
  {
    path: "/rag-chat",
    element: (
      <PageWrapper>
        <Chat assistantId="django_docs_assistant" />
      </PageWrapper>
    ),
  },
  {
    path: "/htmx",
    element: (
      <PageWrapper>
        <Redirect to="/htmx/" />
      </PageWrapper>
    ),
  },
  {
    path: "/tour-guide",
    element: (
      <PageWrapper>
        <TourGuide assistantId="tour_guide_assistant" />
      </PageWrapper>
    ),
  },
  {
    path: "/admin",
    element: (
      <PageWrapper>
        <Redirect to="/admin/" />
      </PageWrapper>
    ),
  },
]);

const App = () => {
  return (
    <MantineProvider theme={theme}>
      <React.StrictMode>
        <RouterProvider router={router} />
      </React.StrictMode>
    </MantineProvider>
  );
};

export default App;
