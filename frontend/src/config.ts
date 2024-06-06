import { OpenAPI } from "./client";

/**
 * Configures the base URL for the AI Assistant API which is path associated with
 * the Django include.
 *
 * @param baseURL Base URL of the AI Assistant API.
 *
 * @example
 * configAiAssistant("ai-assistant");
 */
export function configAiAssistant(baseURL: string) {
  OpenAPI.BASE = baseURL;
}
