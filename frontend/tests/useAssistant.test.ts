import { act, renderHook } from "@testing-library/react";
import { useAssistant } from "../src/hooks";
import { djangoAiAssistantGetAssistant } from "../src/client";

jest.mock("../src/client", () => ({
  djangoAiAssistantGetAssistant: jest
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
      const mockAssistants = [
        { id: 'weather_assistant', name: "Assistant 1" },
        { id: 'movies_assistant', name: "Assistant 2" },
      ];
      (djangoAiAssistantGetAssistant as jest.Mock).mockResolvedValue(
        mockAssistants
      );

      const { result } = renderHook(() => useAssistant({ assistantId: 'weather_assistant' }));

      expect(result.current.assistant).toBeNull();
      expect(result.current.loadingFetchAssistant).toBe(false);

      await act(async () => {
        await result.current.fetchAssistant();
      });

      expect(result.current.assistant).toEqual(mockAssistants);
      expect(result.current.loadingFetchAssistant).toBe(false);
    });

    it("should set loading to false if fetch fails", async () => {
      (djangoAiAssistantGetAssistant as jest.Mock).mockRejectedValue(
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
