/**
 * d3jusdevspace — Axios API Client
 *
 * Centralised HTTP client with:
 *  - Base URL pointing at the Next.js API proxy (`/api/proxy`)
 *  - Automatic `Authorization` header injection for admin routes
 *  - Standardised error normalisation
 */

import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import type { ApiError } from "@/types";

/* ============================================================================
  Configuration
============================================================================ */

const API_BASE_URL = "/api/proxy";

/* ============================================================================
  Client Instance
============================================================================ */

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

/* ============================================================================
  Request Interceptor — attach Authorization token
============================================================================ */

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // In a browser context, retrieve the token from wherever NextAuth stores
    // it (e.g. a cookie decoded via `getSession()`, or localStorage for dev).
    // For now we check localStorage — this will be replaced by NextAuth
    // session handling once auth screens are implemented.
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("d3jusdevspace_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

/* ============================================================================
  Response Interceptor — normalise errors
============================================================================ */

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const apiError: ApiError = {
      detail:
        error.response?.data?.detail ??
        error.message ??
        "An unexpected error occurred.",
      status: error.response?.status ?? 500,
    };

    // Handle 401 globally — clear stale token & redirect to login
    if (apiError.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("d3jusdevspace_token");
      // Don't redirect if already on a public page
      if (window.location.pathname.startsWith("/admin")) {
        window.location.href = "/admin/login";
      }
    }

    return Promise.reject(apiError);
  },
);

export default apiClient;
