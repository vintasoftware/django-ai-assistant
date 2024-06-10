import { useCallback } from "react";
import { useState } from "react";
import {
  AssistantSchema,
  djangoAiAssistantViewsListAssistants,
} from "../client";
import { Callbacks } from "./types";

/**
 * React hook to manage the Assistant resource.
 */
export function useAssistant() {
  const [assistants, setAssistants] = useState<AssistantSchema[] | null>(null);
  const [loadingFetch, setLoadingFetch] = useState<boolean>(false);

  /**
   * Fetches a list of AI assistants.
   *
   * @param onSuccess Callback function called upon successful fetching of assistants.
   * @param onError Callback function called upon error while fetching assistants.
   */
  const fetchAssistants = useCallback(
    async ({ onSuccess, onError }: Callbacks = {}) => {
      try {
        setLoadingFetch(true);
        const fetchedAssistants = await djangoAiAssistantViewsListAssistants();
        setAssistants(fetchedAssistants);
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

  return {
    /**
     * Function to fetch AI assistants from the server.
     */
    fetchResource: fetchAssistants,
    /**
     * List of fetched AI assistants.
     */
    resources: assistants,
    /**
     * Loading state of the fetch operation.
     */
    loadingFetch,
  };
}
