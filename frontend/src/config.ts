import cookie from "cookie";

import { OpenAPI, OpenAPIConfig } from "./client";
import { AxiosRequestConfig } from "axios";

/**
 * Configures the AI Assistant client, such as setting the base URL (which is
 * associated with the Django path include) and request interceptors.
 *
 * By default, this function will add a request interceptor to include the CSRF token
 * in the request headers if it exists. You can override the default request interceptor
 * by providing your own request interceptor function in the configuration object.
 *
 * NOTE: This function must be called in the root of your application before any
 * requests are made to the AI Assistant API.
 *
 * @param props An `OpenAPIConfig` object containing configuration options for the OpenAPI client.
 *
 * @example
 * configAIAssistant({ BASE: "ai-assistant" });
 */
export function configAIAssistant(props: OpenAPIConfig): OpenAPIConfig {
  function defaultRequestInterceptor(request: AxiosRequestConfig) {
    const { csrftoken } = cookie.parse(document.cookie);
    if (request.headers && csrftoken) {
      request.headers["X-CSRFTOKEN"] = csrftoken;
    }
    return request;
  }

  OpenAPI.interceptors.request.use(defaultRequestInterceptor);

  // Apply the configuration options to the OpenAPI client, and allow the user
  // to override the default request interceptor.
  Object.assign(OpenAPI, props);

  return OpenAPI;
}
