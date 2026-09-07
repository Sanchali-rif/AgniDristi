import axios from 'axios'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '')
export const isApiConfigured = Boolean(API_BASE_URL)

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail ?? error.response?.data?.message ?? error.message
    return Promise.reject(new Error(message))
  }
)

export async function apiClient<T>(url: string, config = {}): Promise<T> {
  const response = await axiosClient.get<T>(url, config)
  return response.data
}
