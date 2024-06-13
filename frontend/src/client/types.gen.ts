// This file is auto-generated by @hey-api/openapi-ts

export type AssistantSchema = {
    id: string;
    name: string;
};

export type ThreadSchema = {
    id?: number | null;
    name?: string | null;
    created_at: string;
    updated_at: string;
};

export type ThreadSchemaIn = {
    name?: string;
};

export type ThreadMessageTypeEnum = 'human' | 'ai' | 'generic' | 'system' | 'function' | 'tool';

export type ThreadMessagesSchemaOut = {
    type: ThreadMessageTypeEnum;
    content: string;
};

export type ThreadMessagesSchemaIn = {
    assistant_id: string;
    content: string;
};

export type DjangoAiAssistantViewsListAssistantsResponse = Array<AssistantSchema>;

export type DjangoAiAssistantViewsListThreadsResponse = Array<ThreadSchema>;

export type DjangoAiAssistantViewsCreateThreadData = {
    requestBody: ThreadSchemaIn;
};

export type DjangoAiAssistantViewsCreateThreadResponse = ThreadSchema;

export type DjangoAiAssistantViewsDeleteThreadData = {
    threadId: string;
};

export type DjangoAiAssistantViewsDeleteThreadResponse = void;

export type DjangoAiAssistantViewsListThreadMessagesData = {
    threadId: string;
};

export type DjangoAiAssistantViewsListThreadMessagesResponse = Array<ThreadMessagesSchemaOut>;

export type DjangoAiAssistantViewsCreateThreadMessageData = {
    requestBody: ThreadMessagesSchemaIn;
    threadId: string;
};

export type DjangoAiAssistantViewsCreateThreadMessageResponse = unknown;

export type $OpenApiTs = {
    '/assistants/': {
        get: {
            res: {
                /**
                 * OK
                 */
                200: Array<AssistantSchema>;
            };
        };
    };
    '/threads/': {
        get: {
            res: {
                /**
                 * OK
                 */
                200: Array<ThreadSchema>;
            };
        };
        post: {
            req: DjangoAiAssistantViewsCreateThreadData;
            res: {
                /**
                 * OK
                 */
                200: ThreadSchema;
            };
        };
    };
    '/threads/{thread_id}/': {
        delete: {
            req: DjangoAiAssistantViewsDeleteThreadData;
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
            req: DjangoAiAssistantViewsListThreadMessagesData;
            res: {
                /**
                 * OK
                 */
                200: Array<ThreadMessagesSchemaOut>;
            };
        };
        post: {
            req: DjangoAiAssistantViewsCreateThreadMessageData;
            res: {
                /**
                 * Created
                 */
                201: unknown;
            };
        };
    };
};