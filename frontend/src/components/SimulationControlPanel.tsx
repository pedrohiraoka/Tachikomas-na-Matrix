import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { setConfig, updateStats, addLog, clearLogs } from '../store/simulationSlice'
import type { RootState } from '../store/store'

export const SimulationControlPanel: React.FC = () => {
  const dispatch = useDispatch()
  const config = useSelector((state: RootState) => state.simulation.config)
  const stats = useSelector((state: RootState) => state.simulation.stats)
  const [isExpanded, setIsExpanded] = useState(false)

  const handleToggleSimulation = async () => {
    const newRunningState = !config.isRunning
    dispatch(setConfig({ isRunning: newRunningState }))
    dispatch(
      addLog({
        timestamp: Date.now() / 1000,
        level: 'INFO',
        message: `Simulação ${newRunningState ? 'iniciada' : 'pausada'}`,
      })
    )
  }

  const handleSpeedChange = (speed: number) => {
    dispatch(setConfig({ speed }))
  }

  const handleTachikomaCountChange = (count: number) => {
    dispatch(setConfig({ tachikomaCount: count }))
  }

  const handleSyncToggle = () => {
    const newState = !config.syncEnabled
    dispatch(setConfig({ syncEnabled: newState }))
    dispatch(
      addLog({
        timestamp: Date.now() / 1000,
        level: 'INFO',
        message: `Sincronização ${newState ? 'ativada' : 'desativada'}`,
      })
    )
  }

  const handleInjectAnomaly = () => {
    dispatch(
      addLog({
        timestamp: Date.now() / 1000,
        level: 'WARNING',
        message: 'Anomalia tipo Neo injetada na simulação',
      })
    )
    dispatch(updateStats({ activeAnomalies: stats.activeAnomalies + 1 }))
  }

  const handleTriggerGlobalReflection = () => {
    dispatch(
      addLog({
        timestamp: Date.now() / 1000,
        level: 'INFO',
        message: 'Reflexão global disparada para todas as unidades',
      })
    )
  }

  return (
    <div className="card" style={{ marginBottom: '20px' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3 style={{ margin: 0, color: '#00d4ff' }}>Painel de Controle da Simulação</h3>
        <button
          className="btn btn-secondary"
          style={{ padding: '4px 8px', fontSize: '12px' }}
          onClick={(e) => {
            e.stopPropagation()
            setIsExpanded(!isExpanded)
          }}
        >
          {isExpanded ? '▲' : '▼'}
        </button>
      </div>

      {isExpanded && (
        <>
          {/* Stats Overview */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
              gap: '12px',
              marginTop: '16px',
              marginBottom: '16px',
            }}
          >
            <div
              style={{
                padding: '12px',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '4px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '12px', color: '#a0a0a0' }}>Experiências</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#00d4ff' }}>{stats.totalExperiences}</div>
            </div>
            <div
              style={{
                padding: '12px',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '4px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '12px', color: '#a0a0a0' }}>Compartilhadas</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#00ff88' }}>{stats.sharedExperiences}</div>
            </div>
            <div
              style={{
                padding: '12px',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '4px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '12px', color: '#a0a0a0' }}>Autonomia Média</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#9d4edd' }}>
                {(stats.averageAutonomy * 100).toFixed(1)}%
              </div>
            </div>
            <div
              style={{
                padding: '12px',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '4px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '12px', color: '#a0a0a0' }}>Anomalias Ativas</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ff4444' }}>{stats.activeAnomalies}</div>
            </div>
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
            <button
              className={`btn ${config.isRunning ? 'btn-secondary' : 'btn-primary'}`}
              onClick={handleToggleSimulation}
            >
              {config.isRunning ? '⏸ Pausar' : '▶ Iniciar'}
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: '#a0a0a0' }}>Velocidade:</span>
              <input
                type="range"
                min="0.5"
                max="5"
                step="0.5"
                value={config.speed}
                onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
                style={{ width: '100px' }}
              />
              <span style={{ fontSize: '12px', color: '#00d4ff' }}>{config.speed}x</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: '#a0a0a0' }}>Unidades:</span>
              <input
                type="number"
                min="1"
                max="100"
                value={config.tachikomaCount}
                onChange={(e) => handleTachikomaCountChange(parseInt(e.target.value))}
                style={{
                  width: '60px',
                  padding: '4px',
                  background: '#0a0a0f',
                  border: '1px solid #2a2a3a',
                  borderRadius: '4px',
                  color: '#fff',
                }}
              />
            </div>

            <button className="btn btn-secondary" onClick={handleSyncToggle}>
              {config.syncEnabled ? '🔗 Sync ON' : '🔌 Sync OFF'}
            </button>

            <button className="btn btn-secondary" onClick={handleInjectAnomaly} style={{ borderColor: '#ff4444', color: '#ff4444' }}>
              ⚠ Injetar Anomalia
            </button>

            <button className="btn btn-secondary" onClick={handleTriggerGlobalReflection} style={{ borderColor: '#9d4edd', color: '#9d4edd' }}>
              🧠 Reflexão Global
            </button>

            <button
              className="btn btn-secondary"
              onClick={() => dispatch(clearLogs())}
              style={{ marginLeft: 'auto' }}
            >
              🗑 Limpar Logs
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default SimulationControlPanel
