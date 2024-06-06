import "@mantine/core/styles.css";

import React from "react";
import { createTheme, MantineProvider } from "@mantine/core";
import { Chat } from "@/Chat";
import { configAiAssistant } from "django-ai-assistant-client";

const theme = createTheme({});

configAiAssistant("ai-assistant");

const App = () => {
  return (
    <MantineProvider theme={theme}>
      <Chat />
    </MantineProvider>
  );
};

export default App;
