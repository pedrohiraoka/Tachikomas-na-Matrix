"""
Query Interface - Interface de consulta ao ConceptNet.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class QueryInterface:
    """Interface para consultas ao ConceptNet."""
    
    def __init__(self) -> None:
        logger.info("QueryInterface initialized")
    
    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for concepts."""
        return []
    
    async def expand_query(self, query: str) -> List[str]:
        """Expand query with related terms."""
        return [query]
