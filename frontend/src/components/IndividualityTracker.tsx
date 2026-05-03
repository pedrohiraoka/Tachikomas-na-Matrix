import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface IndividualityTrackerProps {
  tachikomaId: string
  autonomyLevel: number
  divergenceHistory?: Array<{ timestamp: number; divergence: number }>
  personalityVector?: number[]
}

export const IndividualityTracker: React.FC<IndividualityTrackerProps> = ({
  tachikomaId,
  autonomyLevel,
  divergenceHistory = [],
  personalityVector,
}) => {
  const getAutonomyClass = (level: number) => {
    if (level < 0.3) return 'autonomy-low'
    if (level < 0.7) return 'autonomy-medium'
    return 'autonomy-high'
  }

  const getAutonomyLabel = (level: number) => {
    if (level < 0.3) return 'Baixa'
    if (level < 0.7) return 'Média'
    return 'Alta'
  }

  // Generate chart data from history
  const chartData = divergenceHistory.map((h) => ({
    time: new Date(h.timestamp * 1000).toLocaleTimeString(),
    divergence: h.divergence * 100,
  }))

  // Calculate personality traits from vector (simplified)
  const traits = personalityVector
    ? {
        curiosity: personalityVector[0] || 0.5,
        conformity: personalityVector[1] || 0.5,
        creativity: personalityVector[2] || 0.5,
        logic: personalityVector[3] || 0.5,
      }
    : null

  return (
    <div className="card">
      <h3 style={{ margin: '0 0 16px 0', color: '#00d4ff' }}>
        Individualidade: {tachikomaId}
      </h3>

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          padding: '12px',
          background: 'rgba(0,0,0,0.2)',
          borderRadius: '8px',
        }}
      >
        <div>
          <div style={{ fontSize: '12px', color: '#a0a0a0', marginBottom: '4px' }}>Nível de Autonomia</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{(autonomyLevel * 100).toFixed(1)}%</div>
        </div>
        <span className={`autonomy-indicator ${getAutonomyClass(autonomyLevel)}`}>
          {getAutonomyLabel(autonomyLevel)}
        </span>
      </div>

      {chartData.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ fontSize: '14px', color: '#a0a0a0', marginBottom: '8px' }}>Histórico de Divergência</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="time" stroke="#a0a0a0" fontSize={10} />
              <YAxis stroke="#a0a0a0" fontSize={10} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  background: '#12121a',
                  border: '1px solid #2a2a3a',
                  fontSize: '12px',
                }}
              />
              <Line type="monotone" dataKey="divergence" stroke="#00d4ff" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {traits && (
        <div>
          <div style={{ fontSize: '14px', color: '#a0a0a0', marginBottom: '8px' }}>Vetor de Personalidade</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            {Object.entries(traits).map(([trait, value]) => (
              <div
                key={trait}
                style={{
                  padding: '8px',
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '4px',
                }}
              >
                <div style={{ fontSize: '12px', color: '#a0a0a0', textTransform: 'capitalize', marginBottom: '4px' }}>
                  {trait}
                </div>
                <div
                  style={{
                    height: '4px',
                    background: '#2a2a3a',
                    borderRadius: '2px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${Math.abs(value) * 100}%`,
                      height: '100%',
                      background: `linear-gradient(90deg, #00d4ff, #9d4edd)`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {chartData.length === 0 && !traits && (
        <div style={{ textAlign: 'center', padding: '20px', color: '#a0a0a0' }}>
          Dados de individualidade não disponíveis
        </div>
      )}
    </div>
  )
}

export default IndividualityTracker
