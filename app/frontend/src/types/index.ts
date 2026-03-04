// Utility types and helpers

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
}

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
    field: string;
    direction: SortDirection;
}
