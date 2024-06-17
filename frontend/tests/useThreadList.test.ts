import { act, renderHook } from "@testing-library/react";
import { useThreadList } from "../src/hooks";
import {
  djangoAiAssistantCreateThread,
  djangoAiAssistantDeleteThread,
  djangoAiAssistantListThreads,
} from "../src/client";

jest.mock("../src/client", () => ({
  djangoAiAssistantCreateThread: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
  djangoAiAssistantListThreads: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
  djangoAiAssistantDeleteThread: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
}));

describe("useThreadList", () => {
  const mockThreads = [
    {
      id: 2,
      name: "Thread 2",
      created_at: "2024-06-10T00:00:00Z",
      updated_at: "2024-06-10T00:00:00Z",
    },
    {
      id: 1,
      name: "Thread 1",
      created_at: "2024-06-09T00:00:00Z",
      updated_at: "2024-06-09T00:00:00Z",
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should initialize with no threads and loading false", () => {
    const { result } = renderHook(() => useThreadList());

    expect(result.current.threads).toBeNull();
    expect(result.current.loadingFetchThreads).toBe(false);
    expect(result.current.loadingCreateThread).toBe(false);
  });

  describe("fetchThreads", () => {
    it("should fetch threads and update state correctly", async () => {
      (djangoAiAssistantListThreads as jest.Mock).mockResolvedValue(
        mockThreads
      );

      const { result } = renderHook(() => useThreadList());

      expect(result.current.threads).toBeNull();
      expect(result.current.loadingFetchThreads).toBe(false);

      await act(async () => {
        await result.current.fetchThreads();
      });

      expect(result.current.threads).toEqual(mockThreads);
      expect(result.current.loadingFetchThreads).toBe(false);
    });

    it("should set loading to false if fetch fails", async () => {
      (djangoAiAssistantListThreads as jest.Mock).mockRejectedValue(
        new Error("Failed to fetch")
      );

      const { result } = renderHook(() => useThreadList());

      expect(result.current.threads).toBeNull();
      expect(result.current.loadingFetchThreads).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.fetchThreads();
        });
      }).rejects.toThrow("Failed to fetch");

      expect(result.current.threads).toBeNull();
      expect(result.current.loadingFetchThreads).toBe(false);
    });
  });

  describe("createThread", () => {
    it("should create a thread and update state correctly", async () => {
      const mockNewThread = {
        id: 3,
        name: "Thread 3",
        created_at: "2024-06-11T00:00:00Z",
        updated_at: "2024-06-11T00:00:00Z",
      };
      (djangoAiAssistantCreateThread as jest.Mock).mockResolvedValue(
        mockNewThread
      );
      (djangoAiAssistantListThreads as jest.Mock).mockResolvedValue([
        mockNewThread,
        ...mockThreads,
      ]);

      const { result } = renderHook(() => useThreadList());

      expect(result.current.threads).toBeNull();
      expect(result.current.loadingCreateThread).toBe(false);

      await act(async () => {
        const newThread = await result.current.createThread({
          name: "Thread 3",
        });
        expect(newThread).toEqual(mockNewThread);
      });

      expect(result.current.threads).toEqual([mockNewThread, ...mockThreads]);
      expect(result.current.loadingCreateThread).toBe(false);
    });

    it("should create a thread with no name and update state correctly", async () => {
      const mockNewThread = {
        id: 3,
        name: "2024-06-11T00:00:00Z",
        created_at: "2024-06-11T00:00:00Z",
        updated_at: "2024-06-11T00:00:00Z",
      };
      (djangoAiAssistantCreateThread as jest.Mock).mockResolvedValue(
        mockNewThread
      );
      (djangoAiAssistantListThreads as jest.Mock).mockResolvedValue([
        mockNewThread,
        ...mockThreads,
      ]);

      const { result } = renderHook(() => useThreadList());

      expect(result.current.threads).toBeNull();
      expect(result.current.loadingCreateThread).toBe(false);

      await act(async () => {
        const newThread = await result.current.createThread();
        expect(newThread).toEqual(mockNewThread);
      });

      expect(result.current.threads).toEqual([mockNewThread, ...mockThreads]);
      expect(result.current.loadingCreateThread).toBe(false);
    });

    it("should set loading to false if create fails", async () => {
      (djangoAiAssistantCreateThread as jest.Mock).mockRejectedValue(
        new Error("Failed to create")
      );

      const { result } = renderHook(() => useThreadList());

      expect(result.current.threads).toBeNull();
      expect(result.current.loadingCreateThread).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.createThread({ name: "Thread 3" });
        });
      }).rejects.toThrow("Failed to create");

      expect(result.current.threads).toBeNull();
      expect(result.current.loadingCreateThread).toBe(false);
    });
  });

  describe("deleteThread", () => {
    it("should delete a thread and update state correctly", async () => {
      const deletedThreadId = mockThreads[0].id;
      (djangoAiAssistantListThreads as jest.Mock).mockResolvedValue(
        mockThreads.filter((thread) => thread.id !== deletedThreadId)
      );

      const { result } = renderHook(() => useThreadList());

      result.current.threads = mockThreads;

      expect(result.current.threads).toEqual(mockThreads);
      expect(result.current.loadingDeleteThread).toBe(false);

      await act(async () => {
        await result.current.deleteThread({
          threadId: deletedThreadId.toString(),
        });
      });

      expect(result.current.threads).toEqual(
        mockThreads.filter((thread) => thread.id !== deletedThreadId)
      );
      expect(result.current.loadingDeleteThread).toBe(false);
    });

    it("should set loading to false if delete fails", async () => {
      const deletedThreadId = mockThreads[0].id;
      (djangoAiAssistantListThreads as jest.Mock).mockResolvedValue(
        mockThreads.filter((thread) => thread.id !== deletedThreadId)
      );
      (djangoAiAssistantDeleteThread as jest.Mock).mockRejectedValue(
        new Error("Failed to delete")
      );

      const { result } = renderHook(() => useThreadList());

      result.current.threads = mockThreads;

      expect(result.current.threads).toEqual(mockThreads);
      expect(result.current.loadingDeleteThread).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.deleteThread({
            threadId: deletedThreadId.toString(),
          });
        });
      }).rejects.toThrow("Failed to delete");

      expect(result.current.threads).toEqual(mockThreads);
      expect(result.current.loadingDeleteThread).toBe(false);
    });
  });
});
