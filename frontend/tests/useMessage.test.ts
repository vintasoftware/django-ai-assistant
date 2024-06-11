import { act, renderHook } from "@testing-library/react";
import { useMessage } from "../src/hooks";
import {
  djangoAiAssistantViewsCreateThreadMessage,
  djangoAiAssistantViewsListThreadMessages,
} from "../src/client";

jest.mock("../src/client", () => ({
  djangoAiAssistantViewsCreateThreadMessage: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
  djangoAiAssistantViewsListThreadMessages: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
}));

describe("useMessage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockMessages = [
    {
      type: "human",
      content: "Hello!",
    },
    {
      type: "ai",
      content: "Hello! How can I assist you today?",
    },
  ];

  it("should initialize with no messages and loading false", () => {
    const { result } = renderHook(() => useMessage());

    expect(result.current.messages).toBeNull();
    expect(result.current.loadingFetchMessages).toBe(false);
    expect(result.current.loadingCreateMessage).toBe(false);
  });

  describe("fetchMessages", () => {
    it("should fetch messages and update state correctly", async () => {
      (djangoAiAssistantViewsListThreadMessages as jest.Mock).mockResolvedValue(
        mockMessages
      );

      const { result } = renderHook(() => useMessage());

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);

      await act(async () => {
        await result.current.fetchMessages({ threadId: "1" });
      });

      expect(result.current.messages).toEqual(mockMessages);
      expect(result.current.loadingFetchMessages).toBe(false);
    });

    it("should set loading to false if fetch fails", async () => {
      (djangoAiAssistantViewsListThreadMessages as jest.Mock).mockRejectedValue(
        new Error("Failed to fetch")
      );

      const { result } = renderHook(() => useMessage());

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.fetchMessages({ threadId: "1" });
        });
      }).rejects.toThrow("Failed to fetch");

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingFetchMessages).toBe(false);
    });
  });

  describe("createMessage", () => {
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
      (
        djangoAiAssistantViewsCreateThreadMessage as jest.Mock
      ).mockResolvedValue(null);
      (djangoAiAssistantViewsListThreadMessages as jest.Mock).mockResolvedValue(
        [...mockMessages, ...mockNewMessages]
      );

      const { result } = renderHook(() => useMessage());

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);

      await act(async () => {
        await result.current.createMessage({
          threadId: "1",
          assistantId: "1",
          messageTextValue: mockNewMessages[0].content,
        });
      });

      expect(result.current.messages).toEqual([
        ...mockMessages,
        ...mockNewMessages,
      ]);
      expect(result.current.loadingCreateMessage).toBe(false);
    });

    it("should set loading to false if create fails", async () => {
      (
        djangoAiAssistantViewsCreateThreadMessage as jest.Mock
      ).mockRejectedValue(new Error("Failed to create"));

      const { result } = renderHook(() => useMessage());

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.createMessage({
            threadId: "1",
            assistantId: "1",
            messageTextValue: "Hello!",
          });
        });
      }).rejects.toThrow("Failed to create");

      expect(result.current.messages).toBeNull();
      expect(result.current.loadingCreateMessage).toBe(false);
    });
  });
});
