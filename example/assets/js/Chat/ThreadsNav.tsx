import { Text, Group, ActionIcon, Tooltip, rem, Loader } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import classes from "./ThreadsNav.module.css";
import { DjangoThread } from "@/api";
import type { ThreadSchema } from "@/client";

export function ThreadsNav({
  threads,
  selectedThreadId,
  selectThread,
  createThread,
}: {
  threads: ThreadSchema[] | null;
  selectedThreadId: number | null | undefined;
  selectThread: (id: ThreadSchema | null) => void;
  createThread: () => void;
}) {
  const threadLinks = threads?.map((thread) => {
    const isThreadSelected = selectedThreadId && selectedThreadId === thread.id;
    return (
      <a
        href="#"
        onClick={(event) => {
          selectThread(thread);
          event.preventDefault();
        }}
        key={thread.id}
        className={
          classes.threadLink +
          ` ${isThreadSelected ? classes.threadLinkSelected : ""}`
        }
      >
        {thread.name}
      </a>
    );
  });

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
