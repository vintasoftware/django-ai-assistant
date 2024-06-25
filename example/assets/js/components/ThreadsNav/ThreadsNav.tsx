import {
  Text,
  Group,
  ActionIcon,
  Tooltip,
  Loader,
  NavLink,
} from "@mantine/core";
import { useHover } from "@mantine/hooks";
import { IconPlus, IconTrash } from "@tabler/icons-react";
import classes from "./ThreadsNav.module.css";

import { Thread } from "django-ai-assistant-client";

export function ThreadsNav({
  threads,
  selectedThreadId,
  selectThread,
  createThread,
  deleteThread,
}: {
  threads: Thread[] | null;
  selectedThreadId: number | null | undefined;
  selectThread: (thread: Thread | null) => void;
  createThread: () => Promise<Thread>;
  deleteThread: ({ threadId }: { threadId: string }) => Promise<void>;
}) {
  const ThreadNavLink = ({ thread }: { thread: Thread }) => {
    const { hovered, ref } = useHover();

    return (
      <div ref={ref} key={thread.id}>
        <NavLink
          href="#"
          onClick={(event) => {
            selectThread(thread);
            event.preventDefault();
          }}
          label={thread.name}
          active={selectedThreadId === thread.id}
          variant="filled"
          rightSection={
            hovered ? (
              <Tooltip label="Delete thread" withArrow>
                <ActionIcon
                  variant="light"
                  color="red"
                  size="sm"
                  onClick={async () => {
                    await deleteThread({ threadId: thread.id });
                    window.location.reload();
                  }}
                  aria-label="Delete thread"
                >
                  <IconTrash
                    style={{ width: "70%", height: "70%" }}
                    stroke={1.5}
                  />
                </ActionIcon>
              </Tooltip>
            ) : null
          }
        />
      </div>
    );
  };

  const threadLinks = threads?.map((thread) => (
    <ThreadNavLink key={thread.id} thread={thread} />
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
              size="sm"
              onClick={async (e) => {
                const thread = await createThread();
                selectThread(thread);
                e.preventDefault();
              }}
            >
              <IconPlus style={{ width: "70%", height: "70%" }} stroke={1.5} />
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
