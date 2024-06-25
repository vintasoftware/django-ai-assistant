import { useCallback } from "react";
import { useState } from "react";
import {
  AssistantSchema,
  djangoAiAssistantGetAssistant,
} from "../client";

/**
 * React hook to manage an Assistant.
 */
export function useAssistant({ assistantId }: {
  assistantId: string;
}) {
  const [assistant, setAssistant] = useState<AssistantSchema | null>(null);
  const [loadingFetchAssistant, setLoadingFetchAssistant] =
    useState<boolean>(false);

  /**
   * Fetches an AI assistant.
   *
   * @returns A promise that resolves with the fetched AI assistant.
   */
  const fetchAssistant = useCallback(async (): Promise<AssistantSchema> => {
    try {
      setLoadingFetchAssistant(true);
      const fetchedAssistant = await djangoAiAssistantGetAssistant({ assistantId });
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
