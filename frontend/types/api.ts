export type StableErrorDetail = {
  code: string;
  message: string;
};

export type ValidationErrorItem = {
  loc?: Array<string | number>;
  msg?: string;
  type?: string;
};

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
