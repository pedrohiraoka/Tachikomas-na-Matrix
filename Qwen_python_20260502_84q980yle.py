# Exemplo com FastAPI
@app.post("/tachikomas/{tachikoma_id}/experience")
async def log_experience(tachikoma_id: str, experience: ExperienceInput):
    """Registra uma nova experiência para uma Tachikoma"""
    unit = await get_tachikoma(tachikoma_id)
    embedding = await knowledge_engine.encode(experience.text)
    await unit.store_memory(embedding, metadata=experience.metadata)
    
    # Dispara sincronização se marcado como compartilhável
    if experience.shareable:
        await network_protocol.broadcast_experience(tachikoma_id, embedding)
    
    return {"status": "logged", "sync_status": "pending" if experience.shareable else "local"}

@app.get("/network/collective-memory")
async def get_collective_memory(query: str, limit: int = 50):
    """Consulta a memória coletiva da rede Tachikoma"""
    query_embedding = await knowledge_engine.encode(query)
    results = await memory_pool.semantic_search(query_embedding, limit=limit)
    return {"results": results, "source": "collective"}

@app.post("/tachikomas/{tachikoma_id}/reflect")
async def trigger_reflection(tachikoma_id: str, prompt: Optional[str] = None):
    """Dispara ciclo de reflexão para emergência de individualidade"""
    unit = await get_tachikoma(tachikoma_id)
    insights = await emergence_engine.reflect(unit, custom_prompt=prompt)
    
    # Atualiza métricas de autonomia
    new_autonomy = calculate_autonomy_shift(unit, insights)
    await unit.update_autonomy(new_autonomy)
    
    return {
        "insights": insights,
        "autonomy_delta": new_autonomy - unit.autonomy_level,
        "personality_vector_updated": True
    }

@app.websocket("/ws/network/realtime")
async def websocket_network_sync(websocket: WebSocket):
    """WebSocket para visualização em tempo real da rede"""
    await websocket.accept()
    async for event in network_protocol.subscribe_to_events():
        await websocket.send_json(event)