import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface SimulationConfig {
  isRunning: boolean
  speed: number
  tachikomaCount: number
  syncEnabled: boolean
  anomalyRate: number
  reflectionInterval: number
}

interface SimulationState {
  config: SimulationConfig
  stats: {
    totalExperiences: number
    sharedExperiences: number
    averageAutonomy: number
    networkDivergence: number
    activeAnomalies: number
  }
  logs: Array<{ timestamp: number; level: string; message: string }>
  isLoading: boolean
  error: string | null
}

const initialState: SimulationState = {
  config: {
    isRunning: false,
    speed: 1.0,
    tachikomaCount: 10,
    syncEnabled: true,
    anomalyRate: 0.05,
    reflectionInterval: 30,
  },
  stats: {
    totalExperiences: 0,
    sharedExperiences: 0,
    averageAutonomy: 0.5,
    networkDivergence: 0.0,
    activeAnomalies: 0,
  },
  logs: [],
  isLoading: false,
  error: null,
}

const simulationSlice = createSlice({
  name: 'simulation',
  initialState,
  reducers: {
    setConfig(state, action: PayloadAction<Partial<SimulationConfig>>) {
      state.config = { ...state.config, ...action.payload }
    },
    updateStats(state, action: PayloadAction<Partial<SimulationState['stats']>>) {
      state.stats = { ...state.stats, ...action.payload }
    },
    addLog(state, action: PayloadAction<{ timestamp: number; level: string; message: string }>) {
      state.logs.unshift(action.payload)
      if (state.logs.length > 500) {
        state.logs.pop()
      }
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload
    },
    clearLogs(state) {
      state.logs = []
    },
  },
})

export const {
  setConfig,
  updateStats,
  addLog,
  setLoading,
  setError,
  clearLogs,
} = simulationSlice.actions

export default simulationSlice.reducer
