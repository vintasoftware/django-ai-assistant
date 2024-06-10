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
  const [loadingFetch, setLoadingFetch] = useState<boolean>(false);
  const [loadingCreate, setLoadingCreate] = useState<boolean>(false);

  /**
   * Fetches a list of threads.
   *
   * @param onSuccess Callback function called upon successful fetching of threads.
   * @param onError Callback function called upon error while fetching threads.
   */
  const fetchThreads = useCallback(
    async ({ onSuccess, onError }: Callbacks = {}) => {
      try {
        setLoadingFetch(true);
        const fetchedThreads = await djangoAiAssistantViewsListThreads();
        setThreads(fetchedThreads);
        onSuccess?.();
      } catch (error) {
        console.error(error);
        onError?.(error);
      } finally {
        setLoadingFetch(false);
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
        setLoadingCreate(true);
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
        setLoadingCreate(false);
      }
    },
    [fetchThreads]
  );

  return {
    /**
     * Function to fetch threads from the server.
     */
    fetchResource: fetchThreads,
    /**
     * Function to create a new thread.
     */
    createResource: createThread,
    /**
     * Array of fetched threads.
     */
    resources: threads,
    /**
     * Loading state of the fetch operation.
     */
    loadingFetch,
    /**
     * Loading state of the create operation.
     */
    loadingCreate,
  };
}
