"""
Phase 11: Live Research Synthesis Engine - Main Runner

Combines conflict resolution, uncertainty quantification, and insight generation
to produce scientist-ready research summaries that are IMMEDIATELY ACTIONABLE.

This is what scientists NEED RIGHT NOW.
"""

import logging
from typing import List, Dict, Any
from src.synthesis.conflict_resolver import (
    ConflictResolver, Study, get_conflict_resolver
)
from src.synthesis.uncertainty_quantifier import (
    UncertaintyQuantifier, get_uncertainty_quantifier
)
from src.synthesis.insight_generator import (
    InsightGenerator, get_insight_generator
)

logger = logging.getLogger(__name__)


class LiveResearchSynthesizer:
    """
    The complete Phase 11 tool: finds conflicting studies, resolves them,
    quantifies uncertainty, and generates actionable insights.
    
    WHAT IT DOES:
    1. Analyzes your research question
    2. Finds conflicting studies
    3. Determines which to believe
    4. Quantifies how confident you should be
    5. Tells you exactly what to DO
    
    SOLVES:
    - "Which conflicting study should I follow?"
    - "How confident am I in this finding?"
    - "What should I actually DO with this information?"
    - "What research is urgently needed?"
    """

    def __init__(self):
        self.conflict_resolver = get_conflict_resolver()
        self.uncertainty_quantifier = get_uncertainty_quantifier()
        self.insight_generator = get_insight_generator()

    def synthesize(
        self,
        query: str,
        studies: List[Study],
    ) -> Dict[str, Any]:
        """
        Complete synthesis pipeline: detect conflicts → resolve → quantify → generate insights.
        
        Args:
            query: Research question
            studies: List of studies to synthesize
            
        Returns:
            Complete synthesis with actionable recommendations
        """
        
        logger.info(f"🔬 SYNTHESIS START: {query}")
        logger.info(f"   Analyzing {len(studies)} studies...")

        # Step 1: Detect conflicts
        logger.info("   Step 1: Detecting conflicts...")
        conflicts = self.conflict_resolver.detect_conflicts(studies)
        logger.info(f"   ✓ Found {len(conflicts)} conflicts")

        # Step 2: Resolve conflicts
        logger.info("   Step 2: Resolving conflicts...")
        resolutions = self.conflict_resolver.resolve_conflicts()
        logger.info(f"   ✓ Resolved all conflicts")

        # Step 3: Quantify uncertainty
        logger.info("   Step 3: Quantifying uncertainty...")
        uncertainty_score = self.uncertainty_quantifier.calculate_uncertainty(
            finding_id=query,
            study_quality=sum(s.method_quality for s in studies) / len(studies) if studies else 0.5,
            sample_sizes=[s.sample_size for s in studies],
            num_studies=len(studies),
            num_replications=sum(s.replication_count for s in studies),
            effect_consistency=self._calculate_consistency(studies),
            publication_bias_risk=self._estimate_publication_bias(studies),
        )
        logger.info(f"   ✓ Confidence: {uncertainty_score.confidence_level:.0%}")

        # Step 4: Generate insights
        logger.info("   Step 4: Generating actionable insights...")
        insight = self.insight_generator.generate_insight(
            topic=query,
            finding=self._synthesize_finding(studies, resolutions),
            confidence=uncertainty_score.confidence_level,
            num_studies=len(studies),
            num_replications=sum(s.replication_count for s in studies),
            evidence_gaps=self._identify_gaps(studies),
        )
        logger.info(f"   ✓ Action type: {insight.action_type.value}")

        # Compile results
        synthesis = {
            "query": query,
            "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
            )),
            
            # Findings
            "synthesis": self._synthesize_finding(studies, resolutions),
            "confidence_level": uncertainty_score.confidence_level,
            "evidence_level": uncertainty_score.evidence_level.value,
            
            # Conflicts
            "conflicts_detected": len(conflicts),
            "conflicts": [
                {
                    "type": c.conflict_type.value,
                    "study_a": c.study_a.id,
                    "study_b": c.study_b.id,
                    "severity": c.severity,
                }
                for c in conflicts
            ],
            "resolutions": [
                {
                    "conflict": r.conflict_id,
                    "strategy": r.strategy_used.value,
                    "confidence": r.confidence_level,
                    "actionable_insight": r.actionable_insight,
                }
                for r in resolutions
            ],
            
            # Uncertainty
            "uncertainty_breakdown": {
                "quality_score": uncertainty_score.study_quality_score,
                "consistency_score": uncertainty_score.consistency_score,
                "sample_size_score": uncertainty_score.sample_size_score,
                "replication_score": uncertainty_score.replication_score,
                "publication_bias_risk": uncertainty_score.publication_bias_risk,
            },
            "interpretation": uncertainty_score.interpretation,
            
            # Action
            "immediate_action": insight.immediate_action,
            "action_type": insight.action_type.value,
            "implementation_steps": insight.implementation_steps,
            "required_resources": insight.required_resources,
            "timeline": insight.timeline,
            "potential_risks": insight.potential_risks,
            "mitigation_strategies": insight.mitigation_strategies,
            
            # Research gaps
            "research_gaps": {
                "most_critical": insight.research_gap,
                "research_priority": insight.research_priority,
            },
            
            # Meta
            "num_studies_analyzed": len(studies),
            "recommendation": uncertainty_score.recommendation,
        }

        logger.info(f"✨ SYNTHESIS COMPLETE: {query}")
        logger.info(f"   → {uncertainty_score.recommendation}")

        return synthesis

    def _synthesize_finding(
        self,
        studies: List[Study],
        resolutions: List,
    ) -> str:
        """Synthesize main finding from studies and resolutions."""
        
        if not resolutions:
            # Just average the findings
            return f"Based on {len(studies)} studies, the evidence suggests a complex picture. See conflicts below."
        
        # Use the best resolution
        best = resolutions[0]
        for r in resolutions:
            if r.confidence_level > best.confidence_level:
                best = r

        return f"Best evidence-based synthesis: {best.recommended_finding}"

    def _calculate_consistency(self, studies: List[Study]) -> float:
        """Calculate consistency (I² score) across studies."""
        
        if len(studies) < 2:
            return 0.0

        if not all(s.effect_size for s in studies):
            return 0.0

        # Simple heuristic: variability of effect sizes
        effect_sizes = [s.effect_size for s in studies if s.effect_size]
        mean_effect = sum(effect_sizes) / len(effect_sizes)
        variance = sum((e - mean_effect) ** 2 for e in effect_sizes) / len(effect_sizes)
        std_dev = variance ** 0.5

        # I² = 0 (consistent) to 1 (very inconsistent)
        consistency_ratio = std_dev / (abs(mean_effect) + 0.001)
        return min(consistency_ratio, 1.0)

    def _estimate_publication_bias(self, studies: List[Study]) -> float:
        """Estimate risk of publication bias."""
        
        # Heuristic: if many small studies with large effects, high bias risk
        small_studies = sum(1 for s in studies if s.sample_size < 50)
        large_effects = sum(1 for s in studies if s.effect_size and abs(s.effect_size) > 1.0)

        bias_risk = min((small_studies * 0.3) + (large_effects * 0.2), 1.0)
        return bias_risk

    def _identify_gaps(self, studies: List[Study]) -> List[str]:
        """Identify research gaps."""
        
        gaps = []

        # Gap: No replication
        if sum(s.replication_count for s in studies) == 0:
            gaps.append("CRITICAL GAP: No replications found. Urgent need for independent verification.")

        # Gap: Low quality studies
        if sum(1 for s in studies if s.method_quality < 0.5) > len(studies) / 2:
            gaps.append("METHODOLOGICAL GAP: Most studies have low quality. Need rigorous trials.")

        # Gap: Narrow population
        if all(s.metadata.get("population") == studies[0].metadata.get("population") for s in studies):
            gaps.append("POPULATION GAP: All studies on same population. Need generalization studies.")

        # Gap: Heterogeneous effects
        if len(studies) > 2 and self._calculate_consistency(studies) > 0.7:
            gaps.append("MODERATOR GAP: Results vary widely. Need studies to identify why.")

        # Generic gap if no specific gaps
        if not gaps:
            gaps.append("Fine-scale mechanisms still unclear. Consider mechanistic studies.")

        return gaps


def synthesize_research(
    query: str,
    studies: List[Study],
) -> Dict[str, Any]:
    """
    Convenient function to run complete synthesis in one call.
    
    Args:
        query: Research question
        studies: Studies to synthesize
        
    Returns:
        Complete synthesis with recommendations
    """
    synthesizer = LiveResearchSynthesizer()
    return synthesizer.synthesize(query, studies)


def get_synthesizer() -> LiveResearchSynthesizer:
    """Get a synthesizer instance."""
    return LiveResearchSynthesizer()
