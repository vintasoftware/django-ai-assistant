import { act, renderHook } from "@testing-library/react";
import { useMessageList } from "../src/hooks";
import {
  aiCreateThreadMessage,
  aiDeleteThreadMessage,
  aiListThreadMessages,
  ThreadMessage,
} from "../src/client";

jest.mock("../src/client", () => ({
  aiCreateThreadMessage: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
  aiListThreadMessages: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
  aiDeleteThreadMessage: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
}));

describe("useMessageList", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockMessages: ThreadMessage[] = [
    {
      id: "1",
      type: "human",
      content: "Hello!",
    },
    {
      id: "2",
      type: "ai",
      content: "Hello! How can I assist you today?",
    },
  ];

  it("should initialize with no messages and loading false", () => {
    const { result } = renderHook(() => useMessageList({ threadId: null }));

    expect(result.current.messages).toBeNull();
    expect(result.current.loadingFetchMessages).toBe(false);
    expect(result.current.loadingCreateMessage).toBe(false);
  });

  describe("fetchMessages", () => {
    it("should not fetch messages if threadId is null", async () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => { });

      const { result } = renderHook(() => useMessageList({ threadId: null }));

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);

      await act(async () => {
        expect(await result.current.fetchMessages()).toBeNull();
      });

      expect(warnSpy).toHaveBeenCalledWith(
        "threadId is null or undefined. Ignoring fetch operation."
      );

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);

      warnSpy.mockRestore();
    });

    it("should fetch messages and update state correctly", async () => {
      (aiListThreadMessages as jest.Mock).mockResolvedValue(
        mockMessages
      );

      const { result } = renderHook(() => useMessageList({ threadId: "1" }));

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);

      await act(async () => {
        await result.current.fetchMessages();
      });

      expect(result.current.messages).toEqual(mockMessages);
      expect(result.current.loadingFetchMessages).toBe(false);
    });

    it("should set loading to false if fetch fails", async () => {
      (aiListThreadMessages as jest.Mock).mockRejectedValue(
        new Error("Failed to fetch")
      );

      const { result } = renderHook(() => useMessageList({ threadId: "1" }));

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.fetchMessages();
        });
      }).rejects.toThrow("Failed to fetch");

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);
    });
  });

  describe("createMessage", () => {
    it("should not create message if threadId is null", async () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => { });

      const { result } = renderHook(() => useMessageList({ threadId: null }));

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);

      await act(async () => {
        expect(
          await result.current.createMessage({
            assistantId: "1",
            messageTextValue: "Test message",
          })
        ).toBeUndefined();
      });

      expect(warnSpy).toHaveBeenCalledWith(
        "threadId is null or undefined. Ignoring create operation."
      );

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);

      warnSpy.mockRestore();
    });

    it("should create message and update state correctly", async () => {
      const mockNewMessages = [
        {
          type: "human",
          content: "How's the temperature in Recife?",
        },
        {
          type: "ai",
          content: "The current temperature in Recife is 30°C.",
        },
      ];
      (aiCreateThreadMessage as jest.Mock).mockResolvedValue(
        null
      );
      (aiListThreadMessages as jest.Mock).mockResolvedValue([
        ...mockMessages,
        ...mockNewMessages,
      ]);

      const { result } = renderHook(() => useMessageList({ threadId: "1" }));

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);

      await act(async () => {
        expect(
          await result.current.createMessage({
            assistantId: "1",
            messageTextValue: mockNewMessages[0].content,
          })
        ).toBeUndefined();
      });

      expect(result.current.messages).toEqual([
        ...mockMessages,
        ...mockNewMessages,
      ]);
      expect(result.current.loadingCreateMessage).toBe(false);
    });

    it("should set loading to false if create fails", async () => {
      (aiCreateThreadMessage as jest.Mock).mockRejectedValue(
        new Error("Failed to create")
      );

      const { result } = renderHook(() => useMessageList({ threadId: "1" }));

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.createMessage({
            assistantId: "1",
            messageTextValue: "Hello!",
          });
        });
      }).rejects.toThrow("Failed to create");

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);
    });
  });

  describe("deleteMessage", () => {
    it("should not delete message if threadId is null", async () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => { });

      const { result } = renderHook(() => useMessageList({ threadId: null }));

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);

      await act(async () => {
        expect(
          await result.current.deleteMessage({
            messageId: mockMessages[0].id,
          })
        ).toBeUndefined();
      });

      expect(warnSpy).toHaveBeenCalledWith(
        "threadId is null or undefined. Ignoring delete operation."
      );

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingDeleteMessage).toBe(false);

      warnSpy.mockRestore();
    });

    it("should delete a message and update state correctly", async () => {
      const deletedMessageId = mockMessages[0].id;
      (aiListThreadMessages as jest.Mock).mockResolvedValue(
        mockMessages.filter((message) => message.id !== deletedMessageId)
      );

      const { result } = renderHook(() => useMessageList({ threadId: "1" }));

      result.current.messages = mockMessages;

      expect(result.current.messages).toEqual(mockMessages);
      expect(result.current.loadingDeleteMessage).toBe(false);

      await act(async () => {
        await result.current.deleteMessage({
          messageId: deletedMessageId,
        });
      });

      expect(result.current.messages).toEqual(
        mockMessages.filter((message) => message.id !== deletedMessageId)
      );
      expect(result.current.loadingDeleteMessage).toBe(false);
    });

    it("should set loading to false if delete fails", async () => {
      const deletedMessageId = mockMessages[0].id;
      (aiListThreadMessages as jest.Mock).mockResolvedValue(
        mockMessages.filter((message) => message.id !== deletedMessageId)
      );
      (aiDeleteThreadMessage as jest.Mock).mockRejectedValue(
        new Error("Failed to delete")
      );

      const { result } = renderHook(() => useMessageList({ threadId: "1" }));

      result.current.messages = mockMessages;

      expect(result.current.messages).toEqual(mockMessages);
      expect(result.current.loadingDeleteMessage).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.deleteMessage({
            messageId: deletedMessageId,
          });
        });
      }).rejects.toThrow("Failed to delete");

      expect(result.current.messages).toEqual(mockMessages);
      expect(result.current.loadingDeleteMessage).toBe(false);
    });
  });
});
