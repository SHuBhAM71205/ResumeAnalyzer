import { clearAuth, getToken } from "./auth";
import { ApiError } from "./errors";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type LoginPayload = {
  email: string;
  password: string;
};

export type SignupPayload = LoginPayload & {
  name: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    is_active: boolean;
  };
};

export type ResumeMutationResponse = {
  message: string;
  resume_id: string;
};

export type AnalyzeResponse = {
  message: string;
};

type RequestOptions = RequestInit & {
  rawResponse?: boolean;
};

async function parseError(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    const data = (await response.json()) as { detail?: string; err?: string };
    throw new ApiError(response.status, data.detail ?? data.err ?? "Request failed");
  }

  const text = await response.text();
  throw new ApiError(response.status, text || "Request failed");
}

async function request<T>(path: string, init?: RequestOptions): Promise<T> {
  const token = getToken();
  const headers = new Headers(init?.headers);

  if (!headers.has("Content-Type") && !(init?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (response.status === 401) {
    clearAuth();
  }

  if (!response.ok) {
    await parseError(response);
  }

  if (init?.rawResponse) {
    return response as T;
  }

  return (await response.json()) as T;
}

export const api = {
  baseUrl: API_BASE_URL,
  signup: (payload: SignupPayload) =>
    request<AuthResponse>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  login: (payload: LoginPayload) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getProfile: () =>
    request<AuthResponse["user"]>("/user/"),
  getProfileById: (id: string) =>
    request<AuthResponse["user"]>(`/user/${id}`),
  getResume: (userId: string) =>
    request<Response>(`/resume/${userId}`, {
      rawResponse: true,
    }),
  uploadResume: async (userId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<ResumeMutationResponse>(`/resume/upload/${userId}`, {
      method: "POST",
      body: formData,
    });
  },
  updateResume: async (resumeId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<ResumeMutationResponse>(`/resume/update/${resumeId}`, {
      method: "PUT",
      body: formData,
    });
  },
  analyzeResume: (resumeId: string) =>
    request<AnalyzeResponse>(`/resume/analyze/${resumeId}`, {
      method: "POST",
    }),
};
