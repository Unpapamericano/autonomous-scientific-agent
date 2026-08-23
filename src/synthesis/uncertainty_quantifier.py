"""
Phase 11: Uncertainty Quantifier

Quantifies confidence levels in research findings so scientists know
exactly how much to trust each conclusion.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class EvidenceLevel(str, Enum):
    """Evidence strength levels (adapted from GRADE system)."""
    HIGH = "high"  # Further research very unlikely to change
    MODERATE = "moderate"  # Further research may change
    LOW = "low"  # Further research very likely to change
    VERY_LOW = "very_low"  # Insufficient/poor quality evidence


@dataclass
class UncertaintyScore:
    """Quantified uncertainty for a finding."""
    finding_id: str
    confidence_level: float  # 0-1
    evidence_level: EvidenceLevel
    
    # Factors affecting confidence
    study_quality_score: float  # 0-1, based on methodology
    consistency_score: float  # 0-1, how consistent across studies?
    sample_size_score: float  # 0-1, large enough?
    replication_score: float  # 0-1, how many replications?
    publication_bias_risk: float  # 0-1, risk of bias
    
    # Interpretation
    interpretation: str
    recommendation: str  # What should scientist do?


class UncertaintyQuantifier:
    """
    Quantifies scientific uncertainty so findings are actionable.
    
    Scientists NEED this: "How confident am I in this finding?"
    """

    def __init__(self):
        self.scores: List[UncertaintyScore] = []

    def calculate_uncertainty(
        self,
        finding_id: str,
        study_quality: float,
        sample_sizes: List[int],
        num_studies: int,
        num_replications: int,
        effect_consistency: float,
        publication_bias_risk: float = 0.5,
    ) -> UncertaintyScore:
        """
        Calculate comprehensive uncertainty score for a finding.
        
        Args:
            finding_id: ID of the finding
            study_quality: 0-1 score of included studies
            sample_sizes: List of sample sizes from studies
            num_studies: Number of studies examining this question
            num_replications: Number of successful replications
            effect_consistency: 0-1, how consistent are effect sizes? (I² score)
            publication_bias_risk: 0-1, risk of publication bias
            
        Returns:
            UncertaintyScore with detailed breakdown
        """
        # Calculate component scores
        quality_score = study_quality
        sample_score = self._score_sample_sizes(sample_sizes)
        consistency_score = 1.0 - effect_consistency  # Consistency = 1 - heterogeneity
        replication_score = min(num_replications / 3.0, 1.0)  # 3+ reps = perfect
        num_studies_score = min(num_studies / 5.0, 1.0)  # 5+ studies = perfect
        
        # Overall confidence = weighted average
        confidence = (
            0.30 * quality_score +
            0.20 * sample_score +
            0.20 * consistency_score +
            0.15 * replication_score +
            0.10 * num_studies_score +
            -0.05 * publication_bias_risk  # Penalize for bias risk
        )
        confidence = max(0.0, min(1.0, confidence))

        # Determine evidence level (GRADE system)
        evidence_level = self._determine_evidence_level(
            confidence,
            num_studies,
            num_replications,
            quality_score,
            consistency_score,
        )

        # Generate interpretation
        interpretation = self._generate_interpretation(
            confidence,
            evidence_level,
            quality_score,
            consistency_score,
            replication_score,
            publication_bias_risk,
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(confidence, evidence_level)

        score = UncertaintyScore(
            finding_id=finding_id,
            confidence_level=confidence,
            evidence_level=evidence_level,
            study_quality_score=quality_score,
            consistency_score=consistency_score,
            sample_size_score=sample_score,
            replication_score=replication_score,
            publication_bias_risk=publication_bias_risk,
            interpretation=interpretation,
            recommendation=recommendation,
        )

        self.scores.append(score)
        return score

    def _score_sample_sizes(self, sample_sizes: List[int]) -> float:
        """Score based on sample sizes."""
        if not sample_sizes:
            return 0.0

        avg_size = sum(sample_sizes) / len(sample_sizes)
        
        # GRADE: <50 = very low, 50-100 = low, 100-300 = moderate, >300 = high
        if avg_size > 300:
            return 1.0
        elif avg_size > 100:
            return 0.8
        elif avg_size > 50:
            return 0.5
        else:
            return 0.2

    def _determine_evidence_level(
        self,
        confidence: float,
        num_studies: int,
        num_replications: int,
        quality: float,
        consistency: float,
    ) -> EvidenceLevel:
        """Determine evidence level using GRADE-inspired system."""
        
        # Start with HIGH, then downgrade
        level = EvidenceLevel.HIGH

        # Downgrade for low quality
        if quality < 0.5:
            level = EvidenceLevel.LOW
        elif quality < 0.7:
            level = EvidenceLevel.MODERATE

        # Downgrade for single study
        if num_studies == 1:
            level = EvidenceLevel.LOW if level != EvidenceLevel.VERY_LOW else level

        # Downgrade for inconsistency
        if consistency < 0.5:
            level = EvidenceLevel.LOW if level == EvidenceLevel.HIGH else EvidenceLevel.VERY_LOW

        # Downgrade for no replication
        if num_replications == 0:
            level = EvidenceLevel.LOW if level == EvidenceLevel.HIGH else EvidenceLevel.VERY_LOW

        # Upgrade for multiple replications
        if num_replications >= 3:
            level = EvidenceLevel.HIGH if level == EvidenceLevel.MODERATE else level

        return level

    def _generate_interpretation(
        self,
        confidence: float,
        evidence_level: EvidenceLevel,
        quality: float,
        consistency: float,
        replication: float,
        bias_risk: float,
    ) -> str:
        """Generate human-readable interpretation."""
        
        parts = []

        # Confidence
        if confidence > 0.8:
            parts.append("HIGH confidence: This finding is well-supported.")
        elif confidence > 0.6:
            parts.append("MODERATE confidence: This finding is reasonably supported.")
        elif confidence > 0.4:
            parts.append("LOW confidence: This finding has limited support.")
        else:
            parts.append("VERY LOW confidence: This finding is poorly supported.")

        # Evidence level
        parts.append(f"Evidence level: {evidence_level.value}.")

        # Quality
        if quality < 0.5:
            parts.append("⚠️ Included studies had low methodological quality.")
        elif quality > 0.8:
            parts.append("✓ Included studies had high methodological quality.")

        # Consistency
        if consistency < 0.5:
            parts.append("⚠️ Results are heterogeneous (inconsistent across studies).")
        elif consistency > 0.8:
            parts.append("✓ Results are consistent across studies.")

        # Replication
        if replication > 0.8:
            parts.append("✓ Finding has been replicated multiple times.")
        elif replication == 0:
            parts.append("⚠️ Finding has NOT been replicated yet.")

        # Publication bias
        if bias_risk > 0.7:
            parts.append("⚠️ HIGH RISK of publication bias.")
        elif bias_risk < 0.3:
            parts.append("✓ Low risk of publication bias.")

        return " ".join(parts)

    def _generate_recommendation(
        self,
        confidence: float,
        evidence_level: EvidenceLevel,
    ) -> str:
        """Generate actionable recommendation."""
        
        if confidence > 0.8 and evidence_level == EvidenceLevel.HIGH:
            return (
                "✅ STRONG EVIDENCE: Implement this finding with confidence. "
                "Further research unlikely to change conclusion."
            )
        elif confidence > 0.6 and evidence_level in [EvidenceLevel.HIGH, EvidenceLevel.MODERATE]:
            return (
                "✓ REASONABLE EVIDENCE: Implement this finding but monitor for updates. "
                "Further research may refine the recommendation."
            )
        elif confidence > 0.4 and evidence_level == EvidenceLevel.MODERATE:
            return (
                "⚠️ LIMITED EVIDENCE: Use this finding with caution. "
                "Plan for uncertainty. Further research will likely change recommendation."
            )
        else:
            return (
                "❌ INSUFFICIENT EVIDENCE: Do NOT rely on this finding alone. "
                "Either wait for better evidence or test both approaches. "
                "THIS IS A HIGH-PRIORITY RESEARCH GAP."
            )


def get_uncertainty_quantifier() -> UncertaintyQuantifier:
    """Get an uncertainty quantifier instance."""
    return UncertaintyQuantifier()
