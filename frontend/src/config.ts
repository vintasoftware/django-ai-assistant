import { OpenAPI } from "./client";

/**
 * Configures the base URL for the AI Assistant API which is path associated with
 * the Django include.
 *
 * @param baseURL Base URL of the AI Assistant API.
 *
 * @example
 * configAIAssistant({ baseURL: "ai-assistant" });
 */
export function configAIAssistant({ baseURL }: { baseURL: string }) {
  OpenAPI.BASE = baseURL;
}
