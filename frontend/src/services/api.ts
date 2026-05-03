import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface TachikomaState {
  ghost_id: string
  autonomy_level: number
  trust_score: number
  personality_vector: number[]
  last_sync_timestamp: number
  unique_experience_count: number
  shared_experience_count: number
}

export interface MemoryEntry {
  memory_id: string
  tachikoma_id: string
  content: string
  conceptnet_concepts: string[]
  timestamp: number
  shareable: boolean
  reflection_depth: number
  emotional_valence: number
}

export interface ReflectionResult {
  insights: string[]
  autonomy_delta: number
  new_concepts: string[]
  identity_coherence: number
}

export const networkApi = {
  getTachikomas: async () => {
    const response = await api.get('/tachikomas')
    return response.data
  },

  getTachikomaState: async (id: string): Promise<TachikomaState> => {
    const response = await api.get(`/tachikomas/${id}/state`)
    return response.data
  },

  submitExperience: async (id: string, content: string, shareable: boolean = true) => {
    const response = await api.post(`/tachikomas/${id}/experience`, {
      content,
      shareable,
      metadata: {},
    })
    return response.data
  },

  triggerReflection: async (id: string): Promise<ReflectionResult> => {
    const response = await api.post(`/tachikomas/${id}/reflect`)
    return response.data
  },

  searchCollectiveMemory: async (query: string, limit: number = 20) => {
    const response = await api.get('/network/collective-memory', {
      params: { query, limit },
    })
    return response.data
  },
}

export default api
