import cookie from "cookie";

import { OpenAPI } from "./client";
import { AxiosRequestConfig } from "axios";

/**
 * Configures the base URL for the AI Assistant API which is path associated with
 * the Django include.
 *
 * Configures the Axios request to include the CSRF token if it exists.
 *
 * @param baseURL Base URL of the AI Assistant API.
 *
 * @example
 * configAIAssistant({ baseURL: "ai-assistant" });
 */
export function configAIAssistant({ baseURL }: { baseURL: string }) {
  OpenAPI.BASE = baseURL;

  OpenAPI.interceptors.request.use((request: AxiosRequestConfig) => {
    const { csrftoken } = cookie.parse(document.cookie);
    if (request.headers && csrftoken) {
      request.headers["X-CSRFTOKEN"] = csrftoken;
    }
    return request;
  });
}
