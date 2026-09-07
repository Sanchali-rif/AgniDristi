import { axiosClient } from '../lib/axiosClient'

export const backendApi = {
  getSummary: () => axiosClient.get('/dashboard/summary'),
  getObjects: (params?: Record<string, string>) => axiosClient.get('/dashboard/objects', { params }),
  getObjectDetail: (id: string) => axiosClient.get(`/dashboard/objects/${encodeURIComponent(id)}`),
  getAlerts: () => axiosClient.get('/dashboard/alerts'),
  getMonitoring: () => axiosClient.get('/dashboard/monitoring'),
  triggerRun: (triggerType = 'manual') => axiosClient.post('/monitoring/runs/trigger', null, { params: { trigger_type: triggerType } }),
  uploadVnf: (formData: FormData) => axiosClient.post('/vnf/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
}
