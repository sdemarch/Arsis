export interface ApiError {
  readonly error: {
    readonly code: string;
    readonly message: string;
    readonly request_id: string;
  };
}

export interface Page<T> {
  readonly items: T[];
  readonly meta: {
    readonly page: number;
    readonly page_size: number;
    readonly total_items: number;
    readonly total_pages: number;
  };
}
