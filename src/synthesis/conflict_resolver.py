"""
Phase 11: Live Research Synthesis Engine

Resolves conflicting findings in real-time to produce uncertainty-quantified
research summaries that scientists can immediately act on.

Solves: "Which study should I believe when they contradict?"
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Type of conflict between studies."""
    DIRECT_CONTRADICTION = "direct_contradiction"  # A says X, B says not-X
    QUANTITATIVE_DISAGREEMENT = "quantitative_disagreement"  # A: 20%, B: 40%
    SCOPE_DISAGREEMENT = "scope_disagreement"  # Different populations/conditions
    METHODOLOGICAL_WEAKNESS = "methodological_weakness"  # One method is flawed
    MISSING_MODERATOR = "missing_moderator"  # Conflict due to unmeasured variable


class ResolutionStrategy(str, Enum):
    """Strategy for resolving conflicts."""
    WEIGHT_BY_QUALITY = "weight_by_quality"  # Favor higher quality studies
    AVERAGE = "average"  # Simple average of findings
    SUBGROUP_ANALYSIS = "subgroup_analysis"  # Split by moderators
    REQUIRE_REPLICATION = "require_replication"  # Only report if replicated
    FLAG_UNRESOLVED = "flag_unresolved"  # Mark as genuinely uncertain


@dataclass
class Study:
    """A scientific study."""
    id: str
    title: str
    finding: str  # Main finding text
    sample_size: int
    year: int
    effect_size: Optional[float] = None  # Quantitative result
    confidence_interval: Optional[Tuple[float, float]] = None
    method_quality: float = 0.5  # 0-1 score
    replication_count: int = 0  # How many times replicated?
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conflict:
    """A conflict between studies."""
    id: str
    conflict_type: ConflictType
    study_a: Study
    study_b: Study
    severity: float  # 0-1, how serious is the conflict?
    description: str
    possible_explanations: List[str] = field(default_factory=list)


@dataclass
class Resolution:
    """Resolution of a conflict."""
    conflict_id: str
    strategy_used: ResolutionStrategy
    recommended_finding: str
    confidence_level: float  # 0-1, how confident is this resolution?
    explanation: str
    next_research_needed: str  # What should scientists test next?
    actionable_insight: str  # What should practitioners do NOW?


class ConflictResolver:
    """
    Resolves conflicts between contradictory scientific findings.
    
    This is what scientists NEED RIGHT NOW:
    - Finding conflicting studies automatically
    - Determining which to believe
    - Identifying what's actually uncertain
    - Suggesting what research is needed next
    """

    def __init__(self):
        self.conflicts: List[Conflict] = []
        self.resolutions: List[Resolution] = []

    def detect_conflicts(self, studies: List[Study]) -> List[Conflict]:
        """
        Automatically detect conflicts between studies.
        
        Args:
            studies: List of studies to compare
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        for i, study_a in enumerate(studies):
            for study_b in studies[i+1:]:
                conflict = self._compare_studies(study_a, study_b)
                if conflict:
                    conflicts.append(conflict)
                    logger.warning(
                        f"Conflict detected: {study_a.id} vs {study_b.id} "
                        f"({conflict.conflict_type.value})"
                    )

        self.conflicts = conflicts
        return conflicts

    def _compare_studies(self, study_a: Study, study_b: Study) -> Optional[Conflict]:
        """Compare two studies for conflicts."""
        
        # Check for direct contradictions
        if self._are_findings_opposite(study_a.finding, study_b.finding):
            return Conflict(
                id=f"{study_a.id}_vs_{study_b.id}",
                conflict_type=ConflictType.DIRECT_CONTRADICTION,
                study_a=study_a,
                study_b=study_b,
                severity=0.9,
                description=f"Finding A: {study_a.finding}\nFinding B: {study_b.finding}",
                possible_explanations=[
                    "Genuine disagreement in true effect",
                    "Different study populations",
                    "Different measurement methods",
                    "Publication bias in one study",
                ]
            )

        # Check for quantitative disagreement
        if (study_a.effect_size is not None and 
            study_b.effect_size is not None):
            severity = self._quantitative_disagreement_severity(
                study_a.effect_size,
                study_a.confidence_interval,
                study_b.effect_size,
                study_b.confidence_interval
            )
            if severity > 0.5:
                return Conflict(
                    id=f"{study_a.id}_vs_{study_b.id}",
                    conflict_type=ConflictType.QUANTITATIVE_DISAGREEMENT,
                    study_a=study_a,
                    study_b=study_b,
                    severity=severity,
                    description=f"A reports {study_a.effect_size}, B reports {study_b.effect_size}",
                    possible_explanations=[
                        "Legitimate variation in effect size",
                        "Different moderating variables",
                        "Different measurement scales",
                    ]
                )

        # Check for methodological issues
        if study_a.method_quality < 0.3 or study_b.method_quality < 0.3:
            weaker = study_a if study_a.method_quality < study_b.method_quality else study_b
            return Conflict(
                id=f"{study_a.id}_vs_{study_b.id}",
                conflict_type=ConflictType.METHODOLOGICAL_WEAKNESS,
                study_a=study_a,
                study_b=study_b,
                severity=0.7,
                description=f"Study {weaker.id} has low quality ({weaker.method_quality:.0%})",
                possible_explanations=[
                    "Lower quality study may have biases",
                    "Sample size too small",
                    "Insufficient controls",
                ]
            )

        return None

    def _are_findings_opposite(self, finding_a: str, finding_b: str) -> bool:
        """Check if two findings are logically opposite."""
        # Simple heuristic: check for opposite keywords
        opposites = [
            ("increases", "decreases"),
            ("effective", "ineffective"),
            ("reduces risk", "increases risk"),
            ("yes", "no"),
            ("positive", "negative"),
        ]
        
        for pos, neg in opposites:
            if (pos.lower() in finding_a.lower() and neg.lower() in finding_b.lower()) or \
               (neg.lower() in finding_a.lower() and pos.lower() in finding_b.lower()):
                return True
        
        return False

    def _quantitative_disagreement_severity(
        self,
        effect_a: float,
        ci_a: Optional[Tuple[float, float]],
        effect_b: float,
        ci_b: Optional[Tuple[float, float]]
    ) -> float:
        """Calculate severity of quantitative disagreement."""
        # If confidence intervals don't overlap, high severity
        if ci_a and ci_b:
            if ci_a[1] < ci_b[0] or ci_b[1] < ci_a[0]:
                return 0.9

        # Otherwise, scale by relative difference
        relative_diff = abs(effect_a - effect_b) / (abs(effect_a) + abs(effect_b) + 0.001)
        return min(relative_diff, 1.0)

    def resolve_conflicts(self) -> List[Resolution]:
        """
        Resolve all detected conflicts using intelligent strategies.
        
        Returns:
            List of resolutions with actionable insights
        """
        resolutions = []

        for conflict in self.conflicts:
            resolution = self._resolve_single_conflict(conflict)
            resolutions.append(resolution)
            logger.info(
                f"Resolved {conflict.id}: {resolution.strategy_used.value} "
                f"(confidence: {resolution.confidence_level:.0%})"
            )

        self.resolutions = resolutions
        return resolutions

    def _resolve_single_conflict(self, conflict: Conflict) -> Resolution:
        """Resolve a single conflict using the best strategy."""
        
        # Strategy 1: Weight by quality
        if conflict.study_a.method_quality != conflict.study_b.method_quality:
            return self._resolve_by_quality(conflict)

        # Strategy 2: Check for replication
        if conflict.study_a.replication_count > 0 or conflict.study_b.replication_count > 0:
            return self._resolve_by_replication(conflict)

        # Strategy 3: Average if both quantitative
        if conflict.study_a.effect_size and conflict.study_b.effect_size:
            return self._resolve_by_averaging(conflict)

        # Strategy 4: Flag as unresolved
        return self._resolve_as_unresolved(conflict)

    def _resolve_by_quality(self, conflict: Conflict) -> Resolution:
        """Resolve by favoring higher quality study."""
        higher_quality = (
            conflict.study_a if conflict.study_a.method_quality > conflict.study_b.method_quality
            else conflict.study_b
        )
        lower_quality = conflict.study_b if higher_quality == conflict.study_a else conflict.study_a

        return Resolution(
            conflict_id=conflict.id,
            strategy_used=ResolutionStrategy.WEIGHT_BY_QUALITY,
            recommended_finding=higher_quality.finding,
            confidence_level=min(0.9, higher_quality.method_quality + 0.3),
            explanation=(
                f"Study {higher_quality.id} has higher methodological quality "
                f"({higher_quality.method_quality:.0%}) vs {lower_quality.method_quality:.0%}. "
                f"Favor its finding."
            ),
            next_research_needed=(
                f"Replicate {lower_quality.id} with improved methodology to confirm/refute "
                f"{higher_quality.id}'s finding."
            ),
            actionable_insight=(
                f"IF you need to act NOW: Follow {higher_quality.id}'s recommendation. "
                f"But verify with your population, since {lower_quality.id} found opposite."
            )
        )

    def _resolve_by_replication(self, conflict: Conflict) -> Resolution:
        """Resolve by favoring replicated finding."""
        replicated = (
            conflict.study_a if conflict.study_a.replication_count > conflict.study_b.replication_count
            else conflict.study_b
        )
        unreplicated = conflict.study_b if replicated == conflict.study_a else conflict.study_a

        return Resolution(
            conflict_id=conflict.id,
            strategy_used=ResolutionStrategy.REQUIRE_REPLICATION,
            recommended_finding=replicated.finding,
            confidence_level=min(0.95, 0.5 + 0.1 * replicated.replication_count),
            explanation=(
                f"Study {replicated.id} has been replicated {replicated.replication_count} times. "
                f"Study {unreplicated.id} has not been replicated. "
                f"Replication is strong evidence for robustness."
            ),
            next_research_needed=(
                f"Replicate {unreplicated.id} to determine if its finding is a fluke."
            ),
            actionable_insight=(
                f"SAFE TO ACT: Follow {replicated.id}'s finding (replicated {replicated.replication_count}x). "
                f"Monitor for contradictory replication of {unreplicated.id}."
            )
        )

    def _resolve_by_averaging(self, conflict: Conflict) -> Resolution:
        """Resolve by averaging quantitative results."""
        avg_effect = (conflict.study_a.effect_size + conflict.study_b.effect_size) / 2

        return Resolution(
            conflict_id=conflict.id,
            strategy_used=ResolutionStrategy.AVERAGE,
            recommended_finding=f"Best estimate: {avg_effect:.2f} (range: {conflict.study_a.effect_size:.2f}-{conflict.study_b.effect_size:.2f})",
            confidence_level=0.6,
            explanation=(
                f"Neither study definitively better. Average the effects: "
                f"({conflict.study_a.effect_size:.2f} + {conflict.study_b.effect_size:.2f}) / 2 = {avg_effect:.2f}"
            ),
            next_research_needed=(
                f"Identify why estimates differ. Test moderating variables "
                f"(population, dosage, duration, measurement method)."
            ),
            actionable_insight=(
                f"PLAN FOR UNCERTAINTY: True effect likely between {conflict.study_a.effect_size:.2f}-{conflict.study_b.effect_size:.2f}. "
                f"Plan for worst case."
            )
        )

    def _resolve_as_unresolved(self, conflict: Conflict) -> Resolution:
        """Flag conflict as genuinely unresolved."""
        return Resolution(
            conflict_id=conflict.id,
            strategy_used=ResolutionStrategy.FLAG_UNRESOLVED,
            recommended_finding="UNCERTAIN - See explanation",
            confidence_level=0.3,
            explanation=(
                f"Studies {conflict.study_a.id} and {conflict.study_b.id} conflict. "
                f"Possible reasons: {', '.join(conflict.possible_explanations[:3])}"
            ),
            next_research_needed=(
                f"Conduct head-to-head study comparing {conflict.study_a.id} and {conflict.study_b.id} "
                f"using identical methods and populations."
            ),
            actionable_insight=(
                f"⚠️ GENUINE UNCERTAINTY: This question is NOT settled. "
                f"Do NOT rely on either study alone. "
                f"Suggested actions: (1) Wait for replication, (2) Test both approaches, (3) Default to safer option."
            )
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of conflict detection and resolution."""
        return {
            "total_conflicts_detected": len(self.conflicts),
            "conflicts_by_type": {
                ct.value: sum(1 for c in self.conflicts if c.conflict_type == ct)
                for ct in ConflictType
            },
            "resolutions": [
                {
                    "conflict_id": r.conflict_id,
                    "strategy": r.strategy_used.value,
                    "confidence": r.confidence_level,
                    "actionable_insight": r.actionable_insight,
                }
                for r in self.resolutions
            ],
            "unresolved_count": sum(
                1 for r in self.resolutions 
                if r.strategy_used == ResolutionStrategy.FLAG_UNRESOLVED
            ),
        }


def get_conflict_resolver() -> ConflictResolver:
    """Get a conflict resolver instance."""
    return ConflictResolver()
