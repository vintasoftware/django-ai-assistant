import {
  TextInput,
  Code,
  Text,
  Group,
  ActionIcon,
  Tooltip,
  rem,
} from "@mantine/core";
import { IconSearch, IconPlus } from "@tabler/icons-react";
import classes from "./ThreadsNav.module.css";

const threads = [{ label: "Foo" }, { label: "Bar" }];

export function ThreadsNav() {
  const threadLinks = threads.map((thread) => (
    <a
      href="#"
      onClick={(event) => event.preventDefault()}
      key={thread.label}
      className={classes.threadLink}
    >
      {thread.label}
    </a>
  ));

  return (
    <nav className={classes.navbar}>
      <div className={classes.section}></div>

      <TextInput
        placeholder="Search"
        size="xs"
        leftSection={
          <IconSearch
            style={{ width: rem(12), height: rem(12) }}
            stroke={1.5}
          />
        }
        rightSectionWidth={70}
        rightSection={<Code className={classes.searchCode}>Ctrl + K</Code>}
        styles={{ section: { pointerEvents: "none" } }}
        mb="sm"
      />

      <div className={classes.section}>
        <Group className={classes.threadsHeader} justify="space-between">
          <Text fw={500} c="dimmed">
            Threads
          </Text>
          <Tooltip label="Create thread" withArrow position="right">
            <ActionIcon variant="default" size={18}>
              <IconPlus
                style={{ width: rem(12), height: rem(12) }}
                stroke={1.5}
              />
            </ActionIcon>
          </Tooltip>
        </Group>
        <div className={classes.threads}>{threadLinks}</div>
      </div>
    </nav>
  );
}
