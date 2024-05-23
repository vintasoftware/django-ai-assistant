import { Text, Group, ActionIcon, Tooltip, rem, Loader } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import classes from "./ThreadsNav.module.css";
import { DjangoThread } from "@/api";

export function ThreadsNav({
  threads,
  selectThread,
  createThread,
}: {
  threads: DjangoThread[] | null;
  selectThread: (openai_id: string) => void;
  createThread: () => void;
}) {
  const threadLinks = threads?.map((thread) => (
    <a
      href="#"
      onClick={(event) => {
        selectThread(thread.openai_id);
        event.preventDefault();
      }}
      key={thread.openai_id}
      className={classes.threadLink}
    >
      {thread.name}
    </a>
  ));

  return (
    <nav className={classes.navbar}>
      <div className={classes.section}>
        <Group className={classes.threadsHeader} justify="space-between">
          <Text fw={500} c="dimmed">
            Threads
          </Text>
          <Tooltip label="Create thread" withArrow position="right">
            <ActionIcon
              variant="default"
              size={18}
              onClick={(e) => {
                createThread();
                e.preventDefault();
              }}
            >
              <IconPlus
                style={{ width: rem(12), height: rem(12) }}
                stroke={1.5}
              />
            </ActionIcon>
          </Tooltip>
        </Group>

        <div className={classes.threads}>
          {threadLinks ? (
            threadLinks.length ? (
              threadLinks
            ) : (
              <Text className={classes.threadLinkInfo} c="dimmed">
                No threads found
              </Text>
            )
          ) : (
            <Loader className={classes.threadLinkInfo} color="blue" size="sm" />
          )}
        </div>
      </div>
    </nav>
  );
}
