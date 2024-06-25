import { useCallback } from "react";
import { useState } from "react";
import {
  Assistant,
  aiGetAssistant,
} from "../client";

/**
 * React hook to manage an Assistant.
 */
export function useAssistant({ assistantId }: {
  assistantId: string;
}) {
  const [assistant, setAssistant] = useState<Assistant | null>(null);
  const [loadingFetchAssistant, setLoadingFetchAssistant] =
    useState<boolean>(false);

  /**
   * Fetches an AI assistant.
   *
   * @returns A promise that resolves with the fetched AI assistant.
   */
  const fetchAssistant = useCallback(async (): Promise<Assistant> => {
    try {
      setLoadingFetchAssistant(true);
      const fetchedAssistant = await aiGetAssistant({ assistantId });
      setAssistant(fetchedAssistant);
      return fetchedAssistant;
    } finally {
      setLoadingFetchAssistant(false);
    }
  }, [assistantId]);

  return {
    /**
     * Function to fetch an AI assistant from the server.
     */
    fetchAssistant,
    /**
     * Fetched AI assistant.
     */
    assistant,
    /**
     * Loading state of the fetch operation.
     */
    loadingFetchAssistant,
  };
}
