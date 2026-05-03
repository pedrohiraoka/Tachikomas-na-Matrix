"""
Concept Evolution Module

Tracks and manages the evolution of concepts as Tachikomas
propose new relations and modifications to the knowledge graph.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ConceptProposal:
    """Represents a proposed change to the knowledge graph."""
    proposal_id: str
    proposer_id: str  # Tachikoma ghost_id
    concept1: str
    concept2: str
    relation_type: str
    confidence: float
    timestamp: str
    supporting_memories: List[str] = field(default_factory=list)
    votes: Dict[str, float] = field(default_factory=dict)  # ghost_id -> vote weight
    status: str = "pending"  # pending, approved, rejected
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "proposer_id": self.proposer_id,
            "concept1": self.concept1,
            "concept2": self.concept2,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "supporting_memories": self.supporting_memories,
            "votes": self.votes,
            "status": self.status
        }


class ConceptEvolution:
    """
    Manages evolution of the ConceptNet knowledge graph.
    
    Allows Tachikomas to propose new relations based on their
    experiences, with a voting mechanism for approval.
    
    Attributes:
        proposals: Dictionary of pending proposals
        approved_changes: History of approved changes
        approval_threshold: Minimum consensus for approval
    """
    
    def __init__(self, approval_threshold: float = 0.7):
        """
        Initialize concept evolution manager.
        
        Args:
            approval_threshold: Minimum vote ratio for approval
        """
        self.proposals: Dict[str, ConceptProposal] = {}
        self.approved_changes: List[Dict[str, Any]] = []
        self.approval_threshold = approval_threshold
    
    def create_proposal(
        self,
        proposer_id: str,
        concept1: str,
        concept2: str,
        relation_type: str,
        confidence: float,
        supporting_memories: Optional[List[str]] = None
    ) -> ConceptProposal:
        """
        Create a new concept relation proposal.
        
        Args:
            proposer_id: ID of proposing Tachikoma
            concept1: First concept
            concept2: Second concept
            relation_type: Type of relation
            confidence: Confidence score (0-1)
            supporting_memories: List of supporting memory IDs
            
        Returns:
            Created proposal
        """
        proposal_id = self._generate_proposal_id(
            proposer_id, concept1, concept2, relation_type
        )
        
        proposal = ConceptProposal(
            proposal_id=proposal_id,
            proposer_id=proposer_id,
            concept1=concept1,
            concept2=concept2,
            relation_type=relation_type,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            supporting_memories=supporting_memories or [],
            votes={proposer_id: confidence}  # Proposer's initial vote
        )
        
        self.proposals[proposal_id] = proposal
        logger.info(f"Created proposal {proposal_id} by {proposer_id}")
        
        return proposal
    
    def vote_on_proposal(
        self,
        proposal_id: str,
        voter_id: str,
        vote_weight: float
    ) -> bool:
        """
        Cast a vote on a proposal.
        
        Args:
            proposal_id: Proposal to vote on
            voter_id: ID of voting Tachikoma
            vote_weight: Vote weight (positive for approve, negative for reject)
            
        Returns:
            True if vote recorded successfully
        """
        if proposal_id not in self.proposals:
            logger.warning(f"Proposal {proposal_id} not found")
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal.status != "pending":
            logger.warning(f"Proposal {proposal_id} is no longer pending")
            return False
        
        proposal.votes[voter_id] = vote_weight
        logger.debug(f"{voter_id} voted on proposal {proposal_id}: {vote_weight}")
        
        # Check if decision can be made
        self._check_proposal_status(proposal)
        
        return True
    
    def _check_proposal_status(self, proposal: ConceptProposal) -> None:
        """Check if proposal has reached decision threshold."""
        if not proposal.votes:
            return
        
        votes = list(proposal.votes.values())
        total_votes = len(votes)
        
        if total_votes < 2:  # Need at least 2 votes
            return
        
        # Calculate approval ratio
        positive_votes = sum(1 for v in votes if v > 0)
        approval_ratio = positive_votes / total_votes
        
        if approval_ratio >= self.approval_threshold:
            proposal.status = "approved"
            self._approve_proposal(proposal)
        elif approval_ratio < (1 - self.approval_threshold):
            proposal.status = "rejected"
            logger.info(f"Proposal {proposal.proposal_id} rejected")
    
    def _approve_proposal(self, proposal: ConceptProposal) -> None:
        """Process approved proposal."""
        change_record = {
            "proposal": proposal.to_dict(),
            "approved_at": datetime.now().isoformat()
        }
        
        self.approved_changes.append(change_record)
        
        # Remove from pending
        if proposal.proposal_id in self.proposals:
            del self.proposals[proposal.proposal_id]
        
        logger.info(f"Proposal {proposal.proposal_id} approved and recorded")
    
    def get_pending_proposals(self) -> List[ConceptProposal]:
        """Get all pending proposals."""
        return [p for p in self.proposals.values() if p.status == "pending"]
    
    def get_proposal_history(
        self,
        tachikoma_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get proposal history.
        
        Args:
            tachikoma_id: Optional filter by proposer
            
        Returns:
            List of proposal records
        """
        history = self.approved_changes.copy()
        
        if tachikoma_id:
            history = [
                h for h in history
                if h["proposal"]["proposer_id"] == tachikoma_id
            ]
        
        return history
    
    def _generate_proposal_id(
        self,
        proposer_id: str,
        concept1: str,
        concept2: str,
        relation_type: str
    ) -> str:
        """Generate unique proposal ID."""
        content = f"{proposer_id}:{concept1}:{concept2}:{relation_type}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"prop_{timestamp}_{hash_val}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        return {
            "pending_proposals": len([p for p in self.proposals.values() if p.status == "pending"]),
            "approved_total": len(self.approved_changes),
            "approval_threshold": self.approval_threshold
        }
