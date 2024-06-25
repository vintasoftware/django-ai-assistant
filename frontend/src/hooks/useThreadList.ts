import { useCallback } from "react";
import { useState } from "react";
import {
  Thread,
  aiCreateThread,
  aiDeleteThread,
  aiListThreads,
} from "../client";

/**
 * React hook to manage the list, create, and delete of Threads.
 */
export function useThreadList() {
  const [threads, setThreads] = useState<Thread[] | null>(null);
  const [loadingFetchThreads, setLoadingFetchThreads] =
    useState<boolean>(false);
  const [loadingCreateThread, setLoadingCreateThread] =
    useState<boolean>(false);
  const [loadingDeleteThread, setLoadingDeleteThread] =
    useState<boolean>(false);

  /**
   * Fetches a list of threads.
   *
   * @returns A promise that resolves with the fetched list of threads.
   */
  const fetchThreads = useCallback(async (): Promise<Thread[]> => {
    try {
      setLoadingFetchThreads(true);
      const fetchedThreads = await aiListThreads();
      setThreads(fetchedThreads);
      return fetchedThreads;
    } finally {
      setLoadingFetchThreads(false);
    }
  }, []);

  /**
   * Creates a new thread.
   *
   * @returns A promise that resolves with the created thread.
   */
  const createThread = useCallback(
    async ({ name }: { name?: string } = {}): Promise<Thread> => {
      try {
        setLoadingCreateThread(true);
        const thread = await aiCreateThread({
          requestBody: { name: name },
        });
        await fetchThreads();
        return thread;
      } finally {
        setLoadingCreateThread(false);
      }
    },
    [fetchThreads]
  );

  /**
   * Deletes a thread.
   *
   * @param threadId The ID of the thread to delete.
   */
  const deleteThread = useCallback(
    async ({ threadId }: { threadId: string }): Promise<void> => {
      try {
        setLoadingDeleteThread(true);
        await aiDeleteThread({ threadId });
        await fetchThreads();
      } finally {
        setLoadingDeleteThread(false);
      }
    },
    [fetchThreads]
  );

  return {
    /**
     * Function to fetch threads from the server.
     */
    fetchThreads,
    /**
     * Function to create a new thread.
     */
    createThread,
    /**
     * Function to delete a thread.
     */
    deleteThread,
    /**
     * Array of fetched threads.
     */
    threads,
    /**
     * Loading state of the fetch operation.
     */
    loadingFetchThreads,
    /**
     * Loading state of the create operation.
     */
    loadingCreateThread,
    /**
     * Loading state of the delete operation.
     */
    loadingDeleteThread,
  };
}
