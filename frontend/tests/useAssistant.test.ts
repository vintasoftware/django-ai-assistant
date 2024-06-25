import { act, renderHook } from "@testing-library/react";
import { useAssistant } from "../src/hooks";
import { aiGetAssistant } from "../src/client";

jest.mock("../src/client", () => ({
  aiGetAssistant: jest
    .fn()
    .mockImplementation(() => Promise.resolve()),
}));

describe("useAssistant", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should initialize with no assistant and loading false", () => {
    const { result } = renderHook(() => useAssistant({ assistantId: 'weather_assistant' }));

    expect(result.current.assistant).toBeNull();
    expect(result.current.loadingFetchAssistant).toBe(false);
  });

  describe("fetchAssistant", () => {
    it("should fetch assistant and update state correctly", async () => {
      const mockAssistant = { id: 'weather_assistant', name: "Assistant 1" };
      (aiGetAssistant as jest.Mock).mockResolvedValue(
        mockAssistant
      );
      const { result } = renderHook(() => useAssistant({ assistantId: 'weather_assistant' }));
      expect(result.current.assistant).toBeNull();
      expect(result.current.loadingFetchAssistant).toBe(false);
      await act(async () => {
        await result.current.fetchAssistant();
      });
      expect(result.current.assistant).toEqual(mockAssistant);
      expect(result.current.loadingFetchAssistant).toBe(false);
    });

    it("should set loading to false if fetch fails", async () => {
      (aiGetAssistant as jest.Mock).mockRejectedValue(
        new Error("Failed to fetch")
      );

      const { result } = renderHook(() => useAssistant({ assistantId: 'non_existent_assistant' }));

      expect(result.current.assistant).toBeNull();
      expect(result.current.loadingFetchAssistant).toBe(false);

      await expect(async () => {
        await act(async () => {
          await result.current.fetchAssistant();
        });
      }).rejects.toThrow("Failed to fetch");

      expect(result.current.assistant).toBeNull();
      expect(result.current.loadingFetchAssistant).toBe(false);
    });
  });
});
