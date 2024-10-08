// This file is auto-generated by @hey-api/openapi-ts

export type Assistant = {
    id: string;
    name: string;
};

export type Thread = {
    id?: number | null;
    name?: string | null;
    assistant_id?: string | null;
    created_at: string;
    updated_at: string;
};

export type ThreadIn = {
    name?: string;
    assistant_id?: string | null;
};

export type ThreadMessage = {
    id: string;
    type: ThreadMessageTypeEnum;
    content: string;
};

export type ThreadMessageTypeEnum = 'human' | 'ai' | 'generic' | 'system' | 'function' | 'tool';

export type ThreadMessageIn = {
    assistant_id: string;
    content: string;
};

export type AiListAssistantsResponse = Array<Assistant>;

export type AiGetAssistantData = {
    assistantId: string;
};

export type AiGetAssistantResponse = Assistant;

export type AiListThreadsData = {
    assistantId?: string | null;
};

export type AiListThreadsResponse = Array<Thread>;

export type AiCreateThreadData = {
    requestBody: ThreadIn;
};

export type AiCreateThreadResponse = Thread;

export type AiGetThreadData = {
    threadId: unknown;
};

export type AiGetThreadResponse = Thread;

export type AiUpdateThreadData = {
    requestBody: ThreadIn;
    threadId: unknown;
};

export type AiUpdateThreadResponse = Thread;

export type AiDeleteThreadData = {
    threadId: unknown;
};

export type AiDeleteThreadResponse = void;

export type AiListThreadMessagesData = {
    threadId: unknown;
};

export type AiListThreadMessagesResponse = Array<ThreadMessage>;

export type AiCreateThreadMessageData = {
    requestBody: ThreadMessageIn;
    threadId: unknown;
};

export type AiCreateThreadMessageResponse = unknown;

export type AiDeleteThreadMessageData = {
    messageId: unknown;
    threadId: unknown;
};

export type AiDeleteThreadMessageResponse = void;

export type $OpenApiTs = {
    '/assistants/': {
        get: {
            res: {
                /**
                 * OK
                 */
                200: Array<Assistant>;
            };
        };
    };
    '/assistants/{assistant_id}/': {
        get: {
            req: AiGetAssistantData;
            res: {
                /**
                 * OK
                 */
                200: Assistant;
            };
        };
    };
    '/threads/': {
        get: {
            req: AiListThreadsData;
            res: {
                /**
                 * OK
                 */
                200: Array<Thread>;
            };
        };
        post: {
            req: AiCreateThreadData;
            res: {
                /**
                 * OK
                 */
                200: Thread;
            };
        };
    };
    '/threads/{thread_id}/': {
        get: {
            req: AiGetThreadData;
            res: {
                /**
                 * OK
                 */
                200: Thread;
            };
        };
        patch: {
            req: AiUpdateThreadData;
            res: {
                /**
                 * OK
                 */
                200: Thread;
            };
        };
        delete: {
            req: AiDeleteThreadData;
            res: {
                /**
                 * No Content
                 */
                204: void;
            };
        };
    };
    '/threads/{thread_id}/messages/': {
        get: {
            req: AiListThreadMessagesData;
            res: {
                /**
                 * OK
                 */
                200: Array<ThreadMessage>;
            };
        };
        post: {
            req: AiCreateThreadMessageData;
            res: {
                /**
                 * Created
                 */
                201: unknown;
            };
        };
    };
    '/threads/{thread_id}/messages/{message_id}/': {
        delete: {
            req: AiDeleteThreadMessageData;
            res: {
                /**
                 * No Content
                 */
                204: void;
            };
        };
    };
};