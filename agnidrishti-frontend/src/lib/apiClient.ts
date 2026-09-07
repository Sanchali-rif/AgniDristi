import { axiosClient, isApiConfigured, API_BASE_URL } from './axiosClient'

export { isApiConfigured, API_BASE_URL }

export async function apiClient<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = path.startsWith('/') ? path : `/${path}`
  const response = await axiosClient.request<T>({
    url,
    method: (options.method as string) || 'GET',
    data: options.body,
    headers: options.headers as Record<string, string>,
  })
  return response.data
}
