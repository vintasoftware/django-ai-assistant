import "@mantine/core/styles.css";

import {
  Alert,
  Container,
  createTheme,
  List,
  MantineProvider,
  rem,
  ThemeIcon,
  Title,
} from "@mantine/core";
import {
  IconBrandDjango,
  IconCloud,
  IconInfoCircle,
  IconXboxX,
  IconMovie,
} from "@tabler/icons-react";
import { Chat } from "@/components";
import { createBrowserRouter, Link, RouterProvider } from "react-router-dom";
import { configAIAssistant } from "django-ai-assistant-client";
import React from "react";

const theme = createTheme({});

// Relates to path("ai-assistant/", include("django_ai_assistant.urls"))
// which can be found at example/demo/urls.py)
configAIAssistant({ BASE: "ai-assistant" });

const ExampleIndex = () => {
  const [showAlert, setShowAlert] = React.useState<boolean>(true);

  return (
    <Container>
      <Title order={1} my="md">
        Examples
      </Title>

      {showAlert ? (
        <Alert
          variant="light"
          color="orange"
          title="Login Required"
          icon={<IconInfoCircle />}
          withCloseButton
          closeButtonLabel="Dismiss"
          onClose={() => setShowAlert(false)}
          maw={600}
          mb="md"
        >
          You must be logged in to engage with the examples. Please{" "}
          <Link to="/admin" target="_blank">
            log in
          </Link>{" "}
          to continue.
        </Alert>
      ) : null}

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
    element: <ExampleIndex />,
  },
  {
    path: "/weather-chat",
    element: <Chat assistantId="weather_assistant" />,
  },
  {
    path: "/movies-chat",
    element: <Chat assistantId="movie_recommendation_assistant" />,
  },
  {
    path: "/rag-chat",
    element: <Chat assistantId="django_docs_assistant" />,
  },
  {
    path: "/htmx",
    element: <Redirect to="/htmx/" />,
  },
  {
    path: "/admin",
    element: <Redirect to="/admin/" />,
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
