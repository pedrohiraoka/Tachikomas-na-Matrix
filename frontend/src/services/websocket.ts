import { io, Socket } from 'socket.io-client'

export interface NetworkEvent {
  type: 'EXPERIENCE_SHARED' | 'SYNC_COMPLETE' | 'REFLECTION' | 'ANOMALY_DETECTED' | 'AUTONOMY_CHANGE'
  data: any
  timestamp: number
  source_id?: string
}

class WebSocketService {
  private socket: Socket | null = null
  private listeners: Map<string, Set<(event: NetworkEvent) => void>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect(url: string = 'ws://localhost:8000/ws/network/realtime'): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(url, {
          transports: ['websocket'],
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: 1000,
        })

        this.socket.on('connect', () => {
          console.log('[WebSocket] Connected to network')
          this.reconnectAttempts = 0
          resolve()
        })

        this.socket.on('disconnect', (reason) => {
          console.log('[WebSocket] Disconnected:', reason)
        })

        this.socket.on('network_event', (event: NetworkEvent) => {
          this.handleEvent(event)
        })

        this.socket.on('connect_error', (error) => {
          console.error('[WebSocket] Connection error:', error)
          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            reject(error)
          }
        })
      } catch (error) {
        reject(error)
      }
    })
  }

  private handleEvent(event: NetworkEvent) {
    const typeListeners = this.listeners.get(event.type)
    if (typeListeners) {
      typeListeners.forEach(listener => listener(event))
    }

    const allListeners = this.listeners.get('*')
    if (allListeners) {
      allListeners.forEach(listener => listener(event))
    }
  }

  on(eventType: string, callback: (event: NetworkEvent) => void): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType)!.add(callback)
  }

  off(eventType: string, callback: (event: NetworkEvent) => void): void {
    const typeListeners = this.listeners.get(eventType)
    if (typeListeners) {
      typeListeners.delete(callback)
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.listeners.clear()
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

export const websocketService = new WebSocketService()
export default websocketService
