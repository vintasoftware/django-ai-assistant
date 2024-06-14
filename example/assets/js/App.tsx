import "@mantine/core/styles.css";

import { Container, createTheme, MantineProvider } from "@mantine/core";
import { Chat } from "@/components";
import { createBrowserRouter, Link, RouterProvider } from "react-router-dom";
import { configAIAssistant } from "django-ai-assistant-client";

const theme = createTheme({});

// Relates to path("ai-assistant/", include("django_ai_assistant.urls"))
// which can be found at example/demo/urls.py)
configAIAssistant({ baseURL: "ai-assistant" });

const ExampleIndex = () => {
  return (
    <Container>
      <h1>Examples</h1>
      <ul>
        <li>
          <Link to="/weather-chat">Weather Chat</Link>
        </li>
        <li>
          <Link to="/movies-chat">Movie Recommendation Chat</Link>
        </li>
        <li>
          <Link to="/rag-chat">Django Docs RAG Chat</Link>
        </li>
        <li>
          <Link to="/htmx">HTMX demo (no React)</Link>
        </li>
      </ul>
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
