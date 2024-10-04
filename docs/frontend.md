---
search:
  boost: 2 
---

# Frontend

Django AI Assistant has a frontend TypeScript client to facilitate the integration with the Django backend.

## Installation

Install the frontend client using pnpm:

```bash
pnpm install django-ai-assistant-client
```

## Client Configuration

First, you'll need to check what base path you used when setting up the Django AI Assistant backend. The base path is the URL prefix that the Django AI Assistant API is served under. Below the base path would be `ai-assistant`:

```python title="myproject/urls.py" hl_lines="4"
from django.urls import include, path

urlpatterns = [
    path("ai-assistant/", include("django_ai_assistant.urls")),
    ...
]
``` 

Before using the frontend client, import the `configAIAssistant` and configure it with the base path.
If you're using React, a good place to do this is in the `App.tsx` file:

```typescript title="example/assets/js/App.tsx" hl_lines="4"
import { configAIAssistant } from "django-ai-assistant-client";
import React from "react";

configAIAssistant({ BASE: "ai-assistant" });
```

Note in the configuration above, the Django server and the frontend client are using the same base path. If you're using a different base path, make sure to adjust the configuration accordingly.

Now you can use the frontend client to interact with the Django AI Assistant backend. Here's an example of how to create a message:

```typescript
import { aiCreateThreadMessage } from "django-ai-assistant-client";

await aiCreateThreadMessage({
    threadId: 1,
    requestBody: {
        assistant_id: 1,
        message: "What's the weather like today in NYC?"
    }
});
```

### Advanced Client Configuration

By default the frontend client is authenticated via cookies (`CREDENTIALS === 'include'`). You can configure the client differently. Below is the default config:

```typescript
configAIAssistant({
	// Base path of the Django AI Assistant API, can be a relative or full URL:
    BASE: '',
    // Credentials mode for fetch requests:
	CREDENTIALS: 'include',
	// Record<string, unknown> with headers to be sent with each request:
    HEADERS: undefined,
    // Basic authentication username:
    USERNAME: undefined,
    // Basic authentication password:
	PASSWORD: undefined,
    // Token for authentication:
	TOKEN: undefined,
});
```

## Client Functions

The frontend client provides the following functions:

### `aiListAssistants`  
List all assistants the user has access to.  
**Param:** none  
**Return:** a `Promise` that resolves to an `Array` of `Assistant`.

### `aiGetAssistant`  
Get an assistant by ID.  
**Param:** `{ assistantId: string }`  
**Return:** `Promise` that resolves to `Assistant`.

### `aiListThreads`  
List all threads the user has access to.  
**Param:** none  
**Return:** a `Promise` that resolves to an `Array` of `Thread`.

### `aiCreateThread`  
Create a new thread.  
**Param:** `{ requestBody: { name: string } }`  
**Return:** a `Promise` that resolves to a `Thread`.

### `aiGetThread`  
Get a thread by ID.  
**Param:** `{ threadId: string }`  
**Return:** a `Promise` that resolves to a `Thread`.

### `aiUpdateThread`  
Update a thread by ID.  
**Param:** `{ threadId: string, requestBody: { name: string, assistant_id: string } }`  
**Return:** a `Promise` that resolves to a `Thread`.

### `aiDeleteThread`  
Delete a thread by ID.  
**Param:** `{ threadId: string }`  
**Return:** a `Promise` that resolves to `void`.

### `aiListThreadMessages`  
List all messages in a thread.  
**Param:** `{ threadId: string }`  
**Return:** a `Promise` that resolves to an `Array` of `ThreadMessage`.

### `aiCreateThreadMessage`  
Create a new message in a thread.  
**Param:**  
```{ threadId: string, requestBody: { assistant_id: string, message: string } }```  
**Return:** a `Promise` that resolves to `void`.

### `aiDeleteThreadMessage`  
Delete a message in a thread.  
**Param:** `{ threadId: string, messageId: string }`  
**Return:** a `Promise` that resolves to `void`.

!!! note
    These functions correspond to the Django AI Assistant API endpoints. Make sure to read the [API documentation](tutorial.md#using-built-in-api-views) to learn about permissions.

### Type definitions

The type definitions are available at [`frontend/src/client/types.gen.ts`](https://github.com/vintasoftware/django-ai-assistant/blob/main/frontend/src/client/types.gen.ts). You can import the schemas directly from `django-ai-assistant-client` root:

```typescript
import {
    Assistant,
    Thread,
    ThreadMessage
} from "django-ai-assistant-client";
```

## React Hooks

The frontend client also provides React hooks to streamline application building.

!!! warning
    You still have to call [`configAIAssistant`](#client-configuration) on your application before using the hooks.

### `useAssistantList`

React hook to manage the list of Assistants. Use like this:

```typescript
import { useAssistantList } from "django-ai-assistant-client";

export function MyComponent() {
    const {
        assistants,
        fetchAssistants,
        loadingFetchAssistants
    } = useAssistantList();
    // ...
}
```

### `useAssistant`

React hook to manage a single Assistant. Use like this:

```typescript
import { useAssistant } from "django-ai-assistant-client";

export function MyComponent() {
    const {
        assistant,
        fetchAssistant,
        loadingFetchAssistant
    } = useAssistant();
    // ...
}
```

### `useThreadList`

React hook to manage the list, create, and delete of Threads. Use like this:

```typescript
import { useThreadList } from "django-ai-assistant-client";

export function MyComponent() {
    const {
        threads,
        fetchThreads,
        createThread,
        updateThread,
        deleteThread,
        loadingFetchThreads,
        loadingCreateThread,
        loadingUpdateThread,
        loadingDeleteThread
    } = useThreadList();
    // ...
}
```

### `useMessageList`

React hook to manage the list, create, and delete of Messages. Use like this:

```typescript
import { useMessageList, Thread } from "django-ai-assistant-client";

export function MyComponent() {
    const [activeThread, setActiveThread] = useState<Thread | null>(null);
    const {
        messages,
        fetchMessages,
        createMessage,
        deleteMessage,
        loadingFetchMessages,
        loadingCreateMessage,
        loadingDeleteMessage
    } = useMessageList({ threadId: activeThread?.id });
    // ...
}
```

## Example project

The example project makes good use of the React hooks to build LLM-powered applications. Make sure to [check it out](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#readme)!
