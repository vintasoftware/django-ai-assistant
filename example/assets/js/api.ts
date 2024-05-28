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

export async function fetchAssistantID() {
  const response = await csrfFetch("/ai-assistant/assistants/");
  const responseData = await response.json();
  if (!responseData?.data?.length) {
    throw new Error("No assistants found. Please create an assistant on Django side.");
  }
  return responseData.data[0].openai_id as string;
}

export interface DjangoThread {
  openai_id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export async function fetchDjangoThreads() {
  const response = await csrfFetch("/ai-assistant/threads/");
  const responseData = await response.json();
  return responseData.data as DjangoThread[];
}

export async function createThread() {
  const response = await csrfFetch("/ai-assistant/threads/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  const responseData = await response.json();
  return responseData as OpenAI.Beta.Threads.Thread;
}

export async function fetchMessages({ threadId }: { threadId: string }) {
  const response = await csrfFetch(
    `/ai-assistant/threads/${threadId}/messages/`
  );
  const responseData = await response.json();
  const messages = responseData.data as OpenAI.Beta.Threads.Message[];
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
}) {
  await csrfFetch(`/ai-assistant/threads/${threadId}/messages/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content, assistant_id: assistantId }),
  });
}
