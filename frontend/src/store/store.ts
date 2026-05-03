import { configureStore } from '@reduxjs/toolkit'
import networkReducer from './networkSlice'
import memoryReducer from './memorySlice'
import simulationReducer from './simulationSlice'

export const store = configureStore({
  reducer: {
    network: networkReducer,
    memory: memoryReducer,
    simulation: simulationReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
