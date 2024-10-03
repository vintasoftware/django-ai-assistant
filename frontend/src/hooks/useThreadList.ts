import { useCallback } from "react";
import { useState } from "react";
import {
  Thread,
  aiCreateThread,
  aiUpdateThread,
  aiDeleteThread,
  aiListThreads,
} from "../client";

/**
 * React hook to manage the list, create, and delete of Threads.
 * @param assistantId Optional assistant ID to filter threads
 */
export function useThreadList({ assistantId }: { assistantId?: string } = {}) {
  const [threads, setThreads] = useState<Thread[] | null>(null);
  const [loadingFetchThreads, setLoadingFetchThreads] =
    useState<boolean>(false);
  const [loadingCreateThread, setLoadingCreateThread] =
    useState<boolean>(false);
  const [loadingUpdateThread, setLoadingUpdateThread] =
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
      const fetchedThreads = await aiListThreads({ assistantId });
      setThreads(fetchedThreads);
      return fetchedThreads;
    } finally {
      setLoadingFetchThreads(false);
    }
  }, [assistantId]);

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
          requestBody: { name, assistant_id: assistantId },
        });
        await fetchThreads();
        return thread;
      } finally {
        setLoadingCreateThread(false);
      }
    },
    [fetchThreads, assistantId]
  );

  /**
   * Updates a thread.
   *
   * @param threadId The ID of the thread to update.
   * @param name The new name of the thread.
   * @param shouldUpdateAssistantId If true, the assistant ID will be updated.
   * @returns A promise that resolves with the updated thread.
   */
  const updateThread = useCallback(
    async ({ threadId, name, shouldUpdateAssistantId }: { threadId: string, name: string, shouldUpdateAssistantId: boolean }): Promise<Thread> => {
      try {
        setLoadingUpdateThread(true);
        const thread = await aiUpdateThread({
          threadId, requestBody: {
            name,
            assistant_id: shouldUpdateAssistantId ? assistantId : undefined,
          }
        });
        await fetchThreads();
        return thread;
      } finally {
        setLoadingUpdateThread(false);
      }
    },
    [fetchThreads, assistantId]
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
     * Function to update a thread.
     */
    updateThread,
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
     * Loading state of the update operation.
     */
    loadingUpdateThread,
    /**
     * Loading state of the delete operation.
     */
    loadingDeleteThread,
  };
}
