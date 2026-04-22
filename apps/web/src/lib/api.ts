import axios from 'axios';

const ACCESS_TOKEN_KEY = 'rpcp_access_token';

export class APIError extends Error {
  code: string;
  status: number;

  constructor(message: string, code = 'UNKNOWN_ERROR', status = 500) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.status = status;
  }
}

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  timeout: 180000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status ?? 500;
    const code = error.response?.data?.code ?? 'UNKNOWN_ERROR';
    const message = error.response?.data?.message ?? error.message ?? 'Request failed';
    return Promise.reject(new APIError(message, code, status));
  },
);

export async function fetcher<T>(url: string): Promise<T> {
  const response = await api.get(url);
  return response.data.data as T;
}

export async function poster<T>(url: string, payload: unknown): Promise<T> {
  const response = await api.post(url, payload);
  return response.data.data as T;
}

export async function posterForm<T>(url: string, payload: FormData): Promise<T> {
  const response = await api.post(url, payload, { headers: { 'Content-Type': 'multipart/form-data' } });
  return response.data.data as T;
}

export async function putter<T>(url: string, payload: unknown): Promise<T> {
  const response = await api.put(url, payload);
  return response.data.data as T;
}

export async function deleter<T>(url: string): Promise<T> {
  const response = await api.delete(url);
  return response.data.data as T;
}

export function setAccessToken(token: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearAccessToken() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}
