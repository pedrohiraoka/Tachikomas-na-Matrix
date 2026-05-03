import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface MemoryEntry {
  memory_id: string
  tachikoma_id: string
  content: string
  content_embedding: number[]
  conceptnet_concepts: string[]
  timestamp: number
  shareable: boolean
  reflection_depth: number
  emotional_valence: number
  metadata: Record<string, any>
}

interface MemoryState {
  entries: MemoryEntry[]
  searchQuery: string
  searchResults: MemoryEntry[]
  selectedMemory: MemoryEntry | null
  isLoading: boolean
  error: string | null
}

const initialState: MemoryState = {
  entries: [],
  searchQuery: '',
  searchResults: [],
  selectedMemory: null,
  isLoading: false,
  error: null,
}

const memorySlice = createSlice({
  name: 'memory',
  initialState,
  reducers: {
    setEntries(state, action: PayloadAction<MemoryEntry[]>) {
      state.entries = action.payload
    },
    addEntry(state, action: PayloadAction<MemoryEntry>) {
      state.entries.unshift(action.payload)
    },
    setSearchQuery(state, action: PayloadAction<string>) {
      state.searchQuery = action.payload
    },
    setSearchResults(state, action: PayloadAction<MemoryEntry[]>) {
      state.searchResults = action.payload
    },
    setSelectedMemory(state, action: PayloadAction<MemoryEntry | null>) {
      state.selectedMemory = action.payload
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload
    },
  },
})

export const {
  setEntries,
  addEntry,
  setSearchQuery,
  setSearchResults,
  setSelectedMemory,
  setLoading,
  setError,
} = memorySlice.actions

export default memorySlice.reducer
