/**
 * Interface for success and error callbacks.
 */
export interface Callbacks {
  onSuccess?: () => void;
  onError?: (error: unknown) => void;
}
