"""
Agent 2.5A: Intent Scorer

Calculates multi-factor intent scores for leads:
- Signal-based scoring
- Recency decay weighting
- Buying committee detection
"""

from typing import List, Optional
from datetime import datetime

from ..signals.signal_event import SignalEvent
from .data_classes import IntentScore, IntentLabel, ScoringConfig
from ..enrichment.data_classes import EnrichedLead


class IntentScorer:
    """
    Intent Scorer (Agent 2.5A)
    
    Evaluates prospect behavior to determine buying intent.
    Combines signal strength, recency, and buying committee validation.
    """
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        """Initialize the intent scorer."""
        self.config = config or ScoringConfig()
    
    def calculate_intent_score(
        self,
        signals: List[SignalEvent],
        lead: Optional[EnrichedLead] = None,
        company_signals: Optional[List[SignalEvent]] = None,
    ) -> IntentScore:
        """
        Calculate composite intent score.
        
        Args:
            signals: List of signals for the specific lead
            lead: Enriched lead data (optional, for committee detection)
            company_signals: All signals from lead's company (for committee detection)
            
        Returns:
            IntentScore object
        """
        # 1. Base Signal Score (with recency decay)
        raw_score = 0.0
        signal_breakdown = []
        
        for signal in signals:
            # Get base weight for signal type
            base_weight = self.config.signal_weights.get(signal.type.value, 5.0)
            
            # Apply action modifier (e.g., share vs like)
            modifier = 1.0
            if signal.data:
                # Check for event_type (engagement) or other modifiers
                action_type = signal.data.get("event_type") or signal.data.get("round_type")
                if action_type:
                    # Look for exact match or substring match in modifiers
                    for key, val in self.config.action_modifiers.items():
                        if key in str(action_type).lower():
                            modifier = val
                            break
            
            # Apply signal strength (0.0 - 1.0)
            strength_factor = signal.strength
            
            # Apply Recency Decay
            decay = self._calculate_decay(signal.timestamp)
            
            # Calculate final score for this signal
            signal_score = base_weight * modifier * strength_factor * decay
            
            raw_score += signal_score
            signal_breakdown.append({
                "type": signal.type.value,
                "score": round(signal_score, 2),
                "decay": round(decay, 2),
                "timestamp": signal.timestamp.isoformat(),
            })
        
        # 2. Buying Committee Detection
        committee_factor = 1.0
        committee_details = {"detected": False}
        
        if lead and lead.company and company_signals:
            committee_factor = self.detect_buying_committee(
                lead.user_id, 
                company_signals
            )
            if committee_factor > 1.0:
                committee_details = {
                    "detected": True,
                    "multiplier": committee_factor,
                    "reason": "Multiple engaged contacts"
                }
        
        # 3. Final Score Calculation
        final_score = raw_score * committee_factor
        
        # Cap score at 100
        final_score = min(100.0, final_score)
        
        # 4. Determine Label
        label = self._determine_label(final_score)
        
        return IntentScore(
            score=round(final_score, 1),
            label=label,
            signals_score=round(raw_score, 1),
            recency_factor=self._calculate_decay(signals[0].timestamp) if signals else 0.0,
            committee_factor=committee_factor,
            breakdown={
                "signals": signal_breakdown,
                "committee": committee_details,
            }
        )
    
    def detect_buying_committee(
        self, 
        current_user_id: str,
        company_signals: List[SignalEvent]
    ) -> float:
        """
        Detect if multiple people from the same company are engaged.
        
        Args:
            current_user_id: ID of the lead being scored
            company_signals: All signals associated with the company
            
        Returns:
            Multiplier (e.g., 1.5x) if buying committee detected
        """
        if not company_signals:
            return 1.0
            
        # Get unique user IDs engaged in the last 30 days
        active_users = set()
        cutoff = datetime.now().timestamp() - (30 * 24 * 3600)
        
        for signal in company_signals:
            # Check if signal is recent enough
            if signal.timestamp.timestamp() > cutoff:
                if signal.user_id and signal.user_id != current_user_id:
                    active_users.add(signal.user_id)
        
        # If we see other active users, apply multiplier
        if len(active_users) >= 1:
            # 1 other person = 1.2x, 2+ other people = 1.5x
            return 1.5 if len(active_users) >= 2 else 1.2
            
        return 1.0
    
    def _calculate_decay(self, timestamp: datetime) -> float:
        """
        Calculate exponential decay factor based on age.
        Formula: N(t) = N0 * (1/2)^(t / half_life)
        """
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        
        # Prevent future timestamps
        if age_hours < 0:
            age_hours = 0
            
        half_life = self.config.decay_half_life_hours
        
        # Decay factor falls from 1.0 to 0.5 over one half-life
        decay = 0.5 ** (age_hours / half_life)
        
        return decay
    
    def _determine_label(self, score: float) -> IntentLabel:
        """Classify score into High/Medium/Low."""
        if score >= self.config.high_threshold:
            return IntentLabel.HIGH
        elif score >= self.config.medium_threshold:
            return IntentLabel.MEDIUM
        else:
            return IntentLabel.LOW
