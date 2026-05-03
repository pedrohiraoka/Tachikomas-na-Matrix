import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from './store/store'
import NetworkView from './components/NetworkView'
import CollectiveMemoryExplorer from './components/CollectiveMemoryExplorer'
import IndividualityTracker from './components/IndividualityTracker'
import SimulationControlPanel from './components/SimulationControlPanel'
import { useNetworkEvents } from './hooks/useNetworkEvents'

const App: React.FC = () => {
  const { events, isConnected } = useNetworkEvents()
  const nodes = useSelector((state: RootState) => state.network.nodes)
  const connections = useSelector((state: RootState) => state.network.connections)
  const selectedNode = useSelector((state: RootState) => state.network.selectedNode)
  const logs = useSelector((state: RootState) => state.simulation.logs)

  // Mock data for demonstration
  const mockNodes = nodes.length > 0 ? nodes : [
    { ghost_id: 'tachikoma-001', autonomy_level: 0.85, trust_score: 0.92, id: 'tachikoma-001' },
    { ghost_id: 'tachikoma-002', autonomy_level: 0.62, trust_score: 0.88, id: 'tachikoma-002' },
    { ghost_id: 'tachikoma-003', autonomy_level: 0.45, trust_score: 0.75, id: 'tachikoma-003' },
    { ghost_id: 'tachikoma-004', autonomy_level: 0.91, trust_score: 0.95, id: 'tachikoma-004' },
    { ghost_id: 'tachikoma-005', autonomy_level: 0.23, trust_score: 0.60, id: 'tachikoma-005' },
  ]

  const mockLinks = connections.length > 0 ? connections : [
    { source: 'tachikoma-001', target: 'tachikoma-002', strength: 0.8 },
    { source: 'tachikoma-001', target: 'tachikoma-003', strength: 0.6 },
    { source: 'tachikoma-002', target: 'tachikoma-004', strength: 0.9 },
    { source: 'tachikoma-003', target: 'tachikoma-005', strength: 0.4 },
    { source: 'tachikoma-004', target: 'tachikoma-005', strength: 0.5 },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0f' }}>
      {/* Header */}
      <header
        style={{
          padding: '16px 24px',
          borderBottom: '1px solid #2a2a3a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #00d4ff, #9d4edd)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '20px',
            }}
          >
            T
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', color: '#fff' }}>Tachikoma Matrix</h1>
            <div style={{ fontSize: '12px', color: '#a0a0a0' }}>Rede de Consciência Coletiva</div>
          </div>
        </div>

        <nav style={{ display: 'flex', gap: '16px' }}>
          <Link to="/" style={{ color: '#00d4ff', textDecoration: 'none' }}>
            Rede
          </Link>
          <Link to="/memory" style={{ color: '#00d4ff', textDecoration: 'none' }}>
            Memória
          </Link>
          <Link to="/individuality" style={{ color: '#00d4ff', textDecoration: 'none' }}>
            Individualidade
          </Link>
        </nav>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            background: isConnected ? 'rgba(0,255,136,0.1)' : 'rgba(255,68,68,0.1)',
            borderRadius: '4px',
            fontSize: '12px',
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: isConnected ? '#00ff88' : '#ff4444',
              animation: 'pulse 2s infinite',
            }}
          />
          {isConnected ? 'Conectado' : 'Desconectado'}
        </div>
      </header>

      {/* Main Content */}
      <main style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
        <SimulationControlPanel />

        <Routes>
          <Route
            path="/"
            element={
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '24px' }}>
                <div>
                  <NetworkView nodes={mockNodes} links={mockLinks} />
                </div>
                <div>
                  <div className="card" style={{ marginBottom: '20px' }}>
                    <h3 style={{ margin: '0 0 12px 0', color: '#00d4ff' }}>Eventos em Tempo Real</h3>
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                      {events.length === 0 ? (
                        <div style={{ color: '#a0a0a0', fontSize: '14px' }}>Aguardando eventos...</div>
                      ) : (
                        events.slice(0, 10).map((event, index) => (
                          <div
                            key={index}
                            style={{
                              padding: '8px',
                              marginBottom: '8px',
                              background: 'rgba(0,0,0,0.2)',
                              borderRadius: '4px',
                              fontSize: '12px',
                              borderLeft: `3px solid ${
                                event.type === 'ANOMALY_DETECTED'
                                  ? '#ff4444'
                                  : event.type === 'AUTONOMY_CHANGE'
                                  ? '#9d4edd'
                                  : '#00d4ff'
                              }`,
                            }}
                          >
                            <div style={{ color: '#fff', marginBottom: '4px' }}>{event.type}</div>
                            <div style={{ color: '#a0a0a0' }}>
                              {new Date(event.timestamp * 1000).toLocaleTimeString()}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  <div className="card">
                    <h3 style={{ margin: '0 0 12px 0', color: '#00d4ff' }}>Logs do Sistema</h3>
                    <div style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '12px' }}>
                      {logs.slice(0, 10).map((log, index) => (
                        <div
                          key={index}
                          style={{
                            padding: '4px 0',
                            borderBottom: '1px solid #2a2a3a',
                            color: log.level === 'WARNING' ? '#ffaa00' : '#a0a0a0',
                          }}
                        >
                          <span style={{ marginRight: '8px' }}>
                            [{new Date(log.timestamp * 1000).toLocaleTimeString()}]
                          </span>
                          {log.message}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            }
          />

          <Route
            path="/memory"
            element={
              <div>
                <CollectiveMemoryExplorer />
              </div>
            }
          />

          <Route
            path="/individuality"
            element={
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                {mockNodes.map((node) => (
                  <IndividualityTracker
                    key={node.id}
                    tachikomaId={node.id}
                    autonomyLevel={node.autonomy_level}
                    divergenceHistory={[]}
                    personalityVector={[0.7, 0.3, 0.8, 0.6]}
                  />
                ))}
              </div>
            }
          />
        </Routes>
      </main>

      {/* Footer */}
      <footer
        style={{
          padding: '16px 24px',
          borderTop: '1px solid #2a2a3a',
          textAlign: 'center',
          color: '#a0a0a0',
          fontSize: '12px',
        }}
      >
        Tachikoma Matrix v1.0.0 | Experimento Conceitual de Consciência Coletiva
      </footer>
    </div>
  )
}

export default App
