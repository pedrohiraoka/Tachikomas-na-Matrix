import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'

interface Node {
  id: string
  autonomy_level: number
  trust_score: number
  x?: number
  y?: number
}

interface Link {
  source: string
  target: string
  strength: number
}

interface NetworkViewProps {
  nodes: Node[]
  links: Link[]
  onNodeSelect?: (node: Node) => void
  width?: number
  height?: number
}

export const NetworkView: React.FC<NetworkViewProps> = ({
  nodes,
  links,
  onNodeSelect,
  width = 800,
  height = 600,
}) => {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    // Create simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(30))

    // Draw links
    const link = svg
      .append('g')
      .attr('stroke', '#2a2a3a')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke-width', (d: any) => Math.sqrt(d.strength) * 2)

    // Color scale for autonomy
    const autonomyColor = d3.scaleLinear<string>()
      .domain([0, 0.5, 1])
      .range(['#ff4444', '#ffaa00', '#00ff88'])

    // Draw nodes
    const node = svg
      .append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', 20)
      .attr('fill', (d: any) => autonomyColor(d.autonomy_level))
      .attr('cursor', 'pointer')
      .call(
        drag(simulation) as any
      )
      .on('click', (event, d) => {
        if (onNodeSelect) onNodeSelect(d)
      })
      .append('title')
      .text((d: any) => `ID: ${d.id}\nAutonomy: ${(d.autonomy_level * 100).toFixed(1)}%`)

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)
    })

    return () => {
      simulation.stop()
    }
  }, [nodes, links, width, height, onNodeSelect])

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <h3 style={{ margin: '0 0 16px 0', color: '#00d4ff' }}>Rede Tachikoma</h3>
      <svg ref={svgRef} width={width} height={height} style={{ display: 'block', margin: '0 auto' }} />
      <div style={{ marginTop: '12px', display: 'flex', gap: '16px', fontSize: '12px' }}>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: '#ff4444',
              marginRight: '4px',
            }}
          />
          Baixa Autonomia
        </span>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: '#ffaa00',
              marginRight: '4px',
            }}
          />
          Média Autonomia
        </span>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: '#00ff88',
              marginRight: '4px',
            }}
          />
          Alta Autonomia
        </span>
      </div>
    </div>
  )
}

function drag(simulation: any) {
  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    event.subject.fx = event.subject.x
    event.subject.fy = event.subject.y
  }

  function dragged(event: any) {
    event.subject.fx = event.x
    event.subject.fy = event.y
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0)
    event.subject.fx = null
    event.subject.fy = null
  }

  return d3
    .drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended)
}

export default NetworkView
