import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface TachikomaNode {
  ghost_id: string
  autonomy_level: number
  trust_score: number
  personality_vector: number[]
  last_sync_timestamp: number
  unique_experience_count: number
  shared_experience_count: number
}

interface NetworkState {
  nodes: TachikomaNode[]
  connections: Array<{ source: string; target: string; strength: number }>
  selectedNode: TachikomaNode | null
  realtimeEvents: Array<{ type: string; data: any; timestamp: number }>
  isLoading: boolean
  error: string | null
}

const initialState: NetworkState = {
  nodes: [],
  connections: [],
  selectedNode: null,
  realtimeEvents: [],
  isLoading: false,
  error: null,
}

const networkSlice = createSlice({
  name: 'network',
  initialState,
  reducers: {
    setNodes(state, action: PayloadAction<TachikomaNode[]>) {
      state.nodes = action.payload
    },
    setConnections(state, action: PayloadAction<Array<{ source: string; target: string; strength: number }>>) {
      state.connections = action.payload
    },
    setSelectedNode(state, action: PayloadAction<TachikomaNode | null>) {
      state.selectedNode = action.payload
    },
    addRealtimeEvent(state, action: PayloadAction<{ type: string; data: any; timestamp: number }>) {
      state.realtimeEvents.unshift(action.payload)
      if (state.realtimeEvents.length > 100) {
        state.realtimeEvents.pop()
      }
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload
    },
    updateNode(state, action: PayloadAction<Partial<TachikomaNode> & { ghost_id: string }>) {
      const index = state.nodes.findIndex(n => n.ghost_id === action.payload.ghost_id)
      if (index !== -1) {
        state.nodes[index] = { ...state.nodes[index], ...action.payload }
      }
    },
  },
})

export const {
  setNodes,
  setConnections,
  setSelectedNode,
  addRealtimeEvent,
  setLoading,
  setError,
  updateNode,
} = networkSlice.actions

export default networkSlice.reducer
