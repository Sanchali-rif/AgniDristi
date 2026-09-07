import { useMutation } from '@tanstack/react-query'
import { axiosClient } from '../lib/axiosClient'

export interface VNFUploadResult {
  filename: string
  status: string
  mode: string
  batch_id: string
  input_detections: number
  inserted_detections: number
  duplicates: number
  matched_existing: number
  new_candidates: number
  objects_found: number
  new_objects: number
  processing_time_seconds: number
}

export function useVNFUpload() {
  return useMutation({
    mutationFn: async (file: File): Promise<VNFUploadResult> => {
      const form = new FormData()
      form.append('file', file)
      const res = await axiosClient.post<VNFUploadResult>(
        '/vnf/upload',
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      return res.data
    },
  })
}
