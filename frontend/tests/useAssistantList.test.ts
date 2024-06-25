import { act, renderHook } from "@testing-library/react";
import { useAssistantList } from "../src/hooks";
import { aiListAssistants } from "../src/client";

jest.mock("../src/client", () => ({
  aiListAssistants: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
}));

describe("useAssistantList", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should initialize with no assistants and loading false", () => {
    const { result } = renderHook(() => useAssistantList());

    expect(result.current.assistants).toBeNull();
    expect(result.current.loadingFetchAssistants).toBe(false);
  });

  describe("fetchAssistants", () => {
    it("should fetch assistants and update state correctly", async () => {
      const mockAssistants = [
        { id: 1, name: "Assistant 1" },
        { id: 2, name: "Assistant 2" },
      ];
      (aiListAssistants as jest.Mock).mockResolvedValue(
        mockAssistants
      );

      const { result } = renderHook(() => useAssistantList());

      expect(result.current.assistants).toBeNull();
      expect(result.current.loadingFetchAssistants).toBe(false);

      await act(async () => {
        await result.current.fetchAssistants();
      });

      expect(result.current.assistants).toEqual(mockAssistants);
      expect(result.current.loadingFetchAssistants).toBe(false);
    });

    it("should set loading to false if fetch fails", async () => {
      (aiListAssistants as jest.Mock).mockRejectedValue(
        new Error("Failed to fetch")
      );

      const { result } = renderHook(() => useAssistantList());

      expect(result.current.assistants).toBeNull();
      expect(result.current.loadingFetchAssistants).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.fetchAssistants();
        });
      }).rejects.toThrow("Failed to fetch");

      expect(result.current.assistants).toBeNull();
      expect(result.current.loadingFetchAssistants).toBe(false);
    });
  });
});
