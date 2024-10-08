// This file is auto-generated by @hey-api/openapi-ts

export const $Assistant = {
    properties: {
        id: {
            title: 'Id',
            type: 'string'
        },
        name: {
            title: 'Name',
            type: 'string'
        }
    },
    required: ['id', 'name'],
    title: 'Assistant',
    type: 'object'
} as const;

export const $Thread = {
    properties: {
        id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'ID'
        },
        name: {
            anyOf: [
                {
                    maxLength: 255,
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Name'
        },
        assistant_id: {
            anyOf: [
                {
                    maxLength: 255,
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Assistant Id'
        },
        created_at: {
            format: 'date-time',
            title: 'Created At',
            type: 'string'
        },
        updated_at: {
            format: 'date-time',
            title: 'Updated At',
            type: 'string'
        }
    },
    required: ['created_at', 'updated_at'],
    title: 'Thread',
    type: 'object'
} as const;

export const $ThreadIn = {
    properties: {
        name: {
            title: 'Name',
            type: 'string'
        },
        assistant_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Assistant Id'
        }
    },
    title: 'ThreadIn',
    type: 'object'
} as const;

export const $ThreadMessage = {
    properties: {
        id: {
            title: 'Id',
            type: 'string'
        },
        type: {
            '$ref': '#/components/schemas/ThreadMessageTypeEnum'
        },
        content: {
            title: 'Content',
            type: 'string'
        }
    },
    required: ['id', 'type', 'content'],
    title: 'ThreadMessage',
    type: 'object'
} as const;

export const $ThreadMessageTypeEnum = {
    enum: ['human', 'ai', 'generic', 'system', 'function', 'tool'],
    title: 'ThreadMessageTypeEnum',
    type: 'string'
} as const;

export const $ThreadMessageIn = {
    properties: {
        assistant_id: {
            title: 'Assistant Id',
            type: 'string'
        },
        content: {
            title: 'Content',
            type: 'string'
        }
    },
    required: ['assistant_id', 'content'],
    title: 'ThreadMessageIn',
    type: 'object'
} as const;