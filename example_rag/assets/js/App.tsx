import "@mantine/core/styles.css";

import { createTheme, MantineProvider } from "@mantine/core";
import { Chat } from "@/Chat";
import { configAIAssistant } from "django-ai-assistant-client";

const theme = createTheme({});

// Relates to path("ai-assistant/", include("django_ai_assistant.urls"))
// which can be found at example_rag/demo/urls.py)
configAIAssistant({ baseURL: "ai-assistant" });

const App = () => {
  return (
    <MantineProvider theme={theme}>
      <Chat />
    </MantineProvider>
  );
};

export default App;
