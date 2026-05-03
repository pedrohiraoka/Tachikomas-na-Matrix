import React, { useState } from 'react'
import { useCollectiveMemory } from '../hooks/useNetworkEvents'

interface CollectiveMemoryExplorerProps {
  initialQuery?: string
}

export const CollectiveMemoryExplorer: React.FC<CollectiveMemoryExplorerProps> = ({
  initialQuery = '',
}) => {
  const [query, setQuery] = useState(initialQuery)
  const { memories, loading, error } = useCollectiveMemory(query)

  const getEmotionColor = (valence: number) => {
    if (valence > 0.3) return '#00ff88'
    if (valence < -0.3) return '#ff4444'
    return '#ffaa00'
  }

  const formatTimestamp = (ts: number) => {
    return new Date(ts * 1000).toLocaleString('pt-BR')
  }

  return (
    <div className="card">
      <h3 style={{ margin: '0 0 16px 0', color: '#00d4ff' }}>Memória Coletiva</h3>

      <div style={{ marginBottom: '16px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar memórias por conceito..."
          style={{
            width: '100%',
            padding: '10px',
            background: '#0a0a0f',
            border: '1px solid #2a2a3a',
            borderRadius: '4px',
            color: '#fff',
            fontSize: '14px',
          }}
        />
      </div>

      {loading && <div style={{ textAlign: 'center', padding: '20px' }}>Buscando...</div>}

      {error && (
        <div style={{ color: '#ff4444', padding: '10px', background: 'rgba(255,68,68,0.1)', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      {!loading && !error && memories.length === 0 && query.trim() !== '' && (
        <div style={{ textAlign: 'center', padding: '20px', color: '#a0a0a0' }}>
          Nenhuma memória encontrada
        </div>
      )}

      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {memories.map((memory) => (
          <div
            key={memory.memory_id}
            className="memory-entry"
            style={{
              borderColor: getEmotionColor(memory.emotional_valence),
              padding: '12px',
              marginBottom: '8px',
              background: 'rgba(0,0,0,0.2)',
              borderRadius: '4px',
            }}
          >
            <div style={{ fontSize: '14px', marginBottom: '8px' }}>{memory.content}</div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: '12px',
                color: '#a0a0a0',
              }}
            >
              <span>{formatTimestamp(memory.timestamp)}</span>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                {memory.shareable && (
                  <span
                    style={{
                      padding: '2px 6px',
                      background: 'rgba(0,212,255,0.2)',
                      color: '#00d4ff',
                      borderRadius: '3px',
                      fontSize: '11px',
                    }}
                  >
                    Compartilhável
                  </span>
                )}
                <span
                  style={{
                    padding: '2px 6px',
                    background: 'rgba(157,78,221,0.2)',
                    color: '#9d4edd',
                    borderRadius: '3px',
                    fontSize: '11px',
                  }}
                >
                  Profundidade: {(memory.reflection_depth * 100).toFixed(0)}%
                </span>
                <span
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: getEmotionColor(memory.emotional_valence),
                    display: 'inline-block',
                  }}
                  title={`Valência: ${memory.emotional_valence.toFixed(2)}`}
                />
              </div>
            </div>
            {memory.conceptnet_concepts && memory.conceptnet_concepts.length > 0 && (
              <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {memory.conceptnet_concepts.slice(0, 5).map((concept: string) => (
                  <span
                    key={concept}
                    style={{
                      padding: '2px 6px',
                      background: 'rgba(0,255,136,0.1)',
                      color: '#00ff88',
                      borderRadius: '3px',
                      fontSize: '11px',
                      cursor: 'pointer',
                    }}
                    onClick={() => setQuery(concept)}
                  >
                    {concept.replace('/c/en/', '')}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default CollectiveMemoryExplorer
