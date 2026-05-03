# Pseudocódigo simplificado
async def reflection_cycle(tachikoma: TachikomaUnit):
    # 1. Selecionar experiências locais não totalmente sincronizadas
    local_experiences = await tachikoma.get_unique_memories()
    
    # 2. Consultar ConceptNet para conexões semânticas profundas
    concepts = await knowledge_engine.expand_concepts(local_experiences)
    
    # 3. Gerar perguntas existenciais baseadas em lacunas conceituais
    questions = curiosity_engine.generate(concepts, focus=["identity", "purpose", "mortality"])
    
    # 4. Processar respostas via modelo de linguagem leve + embeddings
    reflections = await reflection_model.process(questions, context=tachikoma.memory)
    
    # 5. Atualizar personality_vector com novas dimensões emergentes
    tachikoma.personality_vector = evolve_vector(
        current=tachikoma.personality_vector,
        new_insights=reflections,
        shared_influence=tachikoma.network.trust_weighted_average()
    )
    
    # 6. Decidir se compartilha ou retém a reflexão (autonomia)
    if tachikoma.autonomy_level > threshold and reflections.is_profound():
        await tachikoma.mark_as_private(reflections)  # Não sincronizar
    else:
        await tachikoma.share_with_network(reflections)  # Sincronizar