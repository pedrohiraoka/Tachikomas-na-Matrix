import { useEffect, useState } from 'react'
import websocketService, { NetworkEvent } from '../services/websocket'

export function useNetworkEvents(eventType?: string) {
  const [events, setEvents] = useState<NetworkEvent[]>([])
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const handleConnect = async () => {
      try {
        await websocketService.connect()
        setIsConnected(true)
      } catch (error) {
        console.error('Failed to connect WebSocket:', error)
        setIsConnected(false)
      }
    }

    handleConnect()

    return () => {
      websocketService.disconnect()
    }
  }, [])

  useEffect(() => {
    if (!isConnected) return

    const handleEvent = (event: NetworkEvent) => {
      if (!eventType || event.type === eventType) {
        setEvents(prev => [event, ...prev].slice(0, 100))
      }
    }

    websocketService.on(eventType || '*', handleEvent)

    return () => {
      websocketService.off(eventType || '*', handleEvent)
    }
  }, [isConnected, eventType])

  return { events, isConnected }
}

export function useTachikomaState(ghostId: string) {
  const [state, setState] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchState = async () => {
      try {
        setLoading(true)
        const response = await fetch(`/api/v1/tachikomas/${ghostId}/state`)
        if (!response.ok) throw new Error('Failed to fetch state')
        const data = await response.json()
        setState(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchState()
    const interval = setInterval(fetchState, 5000)

    return () => clearInterval(interval)
  }, [ghostId])

  return { state, loading, error }
}

export function useCollectiveMemory(query: string, limit: number = 20) {
  const [memories, setMemories] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const search = async () => {
      if (!query.trim()) {
        setMemories([])
        return
      }

      try {
        setLoading(true)
        const response = await fetch(
          `/api/v1/network/collective-memory?query=${encodeURIComponent(query)}&limit=${limit}`
        )
        if (!response.ok) throw new Error('Search failed')
        const data = await response.json()
        setMemories(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed')
      } finally {
        setLoading(false)
      }
    }

    const debounce = setTimeout(search, 300)
    return () => clearTimeout(debounce)
  }, [query, limit])

  return { memories, loading, error }
}
