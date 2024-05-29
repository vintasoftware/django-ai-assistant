import cookie from "cookie";
import OpenAI from "openai";

function csrfFetch(url: string, options: RequestInit = {}) {
  const { csrftoken } = cookie.parse(document.cookie);

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      "X-CSRFToken": csrftoken,
    },
    credentials: "include",
  });
}

export async function fetchAssistantID(): Promise<string> {
  const response = await csrfFetch("/ai-assistant/assistants/");
  const responseData = await response.json();
  if (!responseData?.length) {
    throw new Error(
      "No assistants found. Please create an assistant on Django side."
    );
  }
  return responseData[0].openai_id;
}

// TODO: Get typing from Django API
export interface DjangoThread {
  openai_id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export async function fetchDjangoThreads(): Promise<DjangoThread[]> {
  const response = await csrfFetch("/ai-assistant/threads/");
  const responseData = await response.json();
  return responseData;
}

export async function createThread({
  name,
}: {
  name?: string;
} = {}): Promise<DjangoThread> {
  const response = await csrfFetch("/ai-assistant/threads/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });
  const responseData = await response.json();
  return responseData;
}

export async function fetchMessages({
  threadId,
}: {
  threadId: string;
}): Promise<OpenAI.Beta.Threads.Message[]> {
  const response = await csrfFetch(
    `/ai-assistant/threads/${threadId}/messages/`
  );
  const responseData = await response.json();
  const messages = responseData;
  messages.reverse();
  return messages;
}

export async function createMessage({
  threadId,
  assistantId,
  content,
}: {
  threadId: string;
  assistantId: string;
  content: string;
}): Promise<OpenAI.Beta.Threads.Message> {
  const response = await csrfFetch(
    `/ai-assistant/threads/${threadId}/messages/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content, assistant_id: assistantId }),
    }
  );
  const responseData = await response.json();
  return responseData;
}
