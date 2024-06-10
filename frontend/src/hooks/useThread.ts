import { useCallback } from "react";
import { useState } from "react";
import {
  ThreadSchema,
  djangoAiAssistantViewsCreateThread,
  djangoAiAssistantViewsListThreads,
} from "../client";

import { Callbacks } from "./types";

/**
 * React hook to manage the Thread resource.
 */
export function useThread() {
  const [threads, setThreads] = useState<ThreadSchema[] | null>(null);
  const [loadingFetchThreads, setLoadingFetchThreads] =
    useState<boolean>(false);
  const [loadingCreateThread, setLoadingCreateThread] =
    useState<boolean>(false);

  /**
   * Fetches a list of threads.
   *
   * @param onSuccess Callback function called upon successful fetching of threads.
   * @param onError Callback function called upon error while fetching threads.
   */
  const fetchThreads = useCallback(
    async ({ onSuccess, onError }: Callbacks = {}) => {
      try {
        setLoadingFetchThreads(true);
        const fetchedThreads = await djangoAiAssistantViewsListThreads();
        setThreads(fetchedThreads);
        onSuccess?.();
      } catch (error) {
        console.error(error);
        onError?.(error);
      } finally {
        setLoadingFetchThreads(false);
      }
    },
    []
  );

  /**
   * Creates a new thread.
   *
   * @param onSuccess Callback function called upon successful creation of thread.
   * @param onError Callback function called upon error while creating thread.
   * @returns The created thread, or null if creation fails.
   */
  const createThread = useCallback(
    async ({
      name,
      onSuccess,
      onError,
    }: { name?: string } & Callbacks = {}): Promise<ThreadSchema | null> => {
      try {
        setLoadingCreateThread(true);
        const thread = await djangoAiAssistantViewsCreateThread({
          requestBody: { name },
        });
        await fetchThreads();
        onSuccess?.();
        return thread;
      } catch (error) {
        console.error(error);
        onError?.(error);
        return null;
      } finally {
        setLoadingCreateThread(false);
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
  };
}
