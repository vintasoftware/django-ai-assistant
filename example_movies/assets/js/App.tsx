import "@mantine/core/styles.css";

import React from "react";
import { createTheme, MantineProvider } from "@mantine/core";
import { Chat } from "@/Chat";

const theme = createTheme({});

const App = () => {
  return (
    <MantineProvider theme={theme}>
      <Chat />
    </MantineProvider>
  );
};

export default App;
