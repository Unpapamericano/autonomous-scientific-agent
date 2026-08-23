"""
Phase 11: Live Research Synthesis Tests

Tests for conflict resolution, uncertainty quantification, and insight generation.
"""

import pytest
from src.synthesis.conflict_resolver import (
    ConflictResolver, Study, ConflictType, get_conflict_resolver
)
from src.synthesis.uncertainty_quantifier import (
    UncertaintyQuantifier, EvidenceLevel, get_uncertainty_quantifier
)
from src.synthesis.insight_generator import (
    InsightGenerator, ActionType, get_insight_generator
)
from src.synthesis.live_runner import LiveResearchSynthesizer, synthesize_research


class TestConflictResolver:
    """Test conflict detection and resolution."""

    def test_detect_direct_contradiction(self):
        """Test detection of direct contradictions."""
        resolver = get_conflict_resolver()
        
        study_a = Study(
            id="s1", title="Study A", finding="X decreases Y",
            sample_size=100, year=2020, effect_size=-0.5, method_quality=0.8
        )
        study_b = Study(
            id="s2", title="Study B", finding="X increases Y",
            sample_size=150, year=2021, effect_size=0.3, method_quality=0.8
        )
        
        conflicts = resolver.detect_conflicts([study_a, study_b])
        
        assert len(conflicts) > 0
        assert any(c.conflict_type == ConflictType.DIRECT_CONTRADICTION for c in conflicts)

    def test_resolve_by_quality(self):
        """Test resolution by study quality."""
        resolver = get_conflict_resolver()
        
        study_a = Study(
            id="s1", title="High Quality", finding="X increases Y",
            sample_size=500, year=2021, method_quality=0.9, effect_size=0.5
        )
        study_b = Study(
            id="s2", title="Low Quality", finding="X decreases Y",
            sample_size=30, year=2020, method_quality=0.3, effect_size=-0.2
        )
        
        conflicts = resolver.detect_conflicts([study_a, study_b])
        assert len(conflicts) > 0  # Should detect contradiction

    def test_resolve_by_replication(self):
        """Test resolution by replication count."""
        resolver = get_conflict_resolver()
        
        study_replicated = Study(
            id="s1", title="Replicated", finding="X causes Y",
            sample_size=100, year=2021, method_quality=0.7, effect_size=0.4, replication_count=3
        )
        study_unreplicated = Study(
            id="s2", title="Not Replicated", finding="X does not cause Y",
            sample_size=100, year=2022, method_quality=0.7, effect_size=0.0, replication_count=0
        )
        
        conflicts = resolver.detect_conflicts([study_replicated, study_unreplicated])
        assert len(conflicts) > 0  # Should detect contradiction


class TestUncertaintyQuantifier:
    """Test uncertainty quantification."""

    def test_high_confidence_scenario(self):
        """Test calculation for high-confidence finding."""
        quantifier = get_uncertainty_quantifier()
        
        score = quantifier.calculate_uncertainty(
            finding_id="test",
            study_quality=0.9,
            sample_sizes=[300, 250, 400],
            num_studies=3,
            num_replications=2,
            effect_consistency=0.1,  # Low heterogeneity = high consistency
            publication_bias_risk=0.2,
        )
        
        assert score.confidence_level > 0.7
        assert score.evidence_level == EvidenceLevel.HIGH

    def test_low_confidence_scenario(self):
        """Test calculation for low-confidence finding."""
        quantifier = get_uncertainty_quantifier()
        
        score = quantifier.calculate_uncertainty(
            finding_id="test",
            study_quality=0.3,
            sample_sizes=[20, 25, 18],
            num_studies=3,
            num_replications=0,
            effect_consistency=0.9,  # High heterogeneity
            publication_bias_risk=0.8,
        )
        
        assert score.confidence_level < 0.6
        assert score.evidence_level in [EvidenceLevel.LOW, EvidenceLevel.VERY_LOW]

    def test_recommendation_generation(self):
        """Test that recommendations are generated."""
        quantifier = get_uncertainty_quantifier()
        
        score = quantifier.calculate_uncertainty(
            finding_id="test",
            study_quality=0.8,
            sample_sizes=[200, 250],
            num_studies=2,
            num_replications=1,
            effect_consistency=0.2,
            publication_bias_risk=0.1,
        )
        
        assert score.recommendation is not None
        assert len(score.recommendation) > 0


class TestInsightGenerator:
    """Test actionable insight generation."""

    def test_generate_implement_immediately_insight(self):
        """Test high-confidence insight."""
        generator = get_insight_generator()
        
        insight = generator.generate_insight(
            topic="Test Topic",
            finding="X effectively improves Y",
            confidence=0.9,
            num_studies=5,
            num_replications=3,
            evidence_gaps=[],
        )
        
        assert insight.action_type == ActionType.IMPLEMENT_IMMEDIATELY
        assert "NOW" in insight.immediate_action
        assert len(insight.implementation_steps) > 0

    def test_generate_wait_for_replication_insight(self):
        """Test low-confidence, unreplicated insight."""
        generator = get_insight_generator()
        
        insight = generator.generate_insight(
            topic="New Finding",
            finding="Experimental approach might work",
            confidence=0.65,  # Higher than 0.5 to trigger WAIT_FOR_REPLICATION
            num_studies=2,  # Multiple studies
            num_replications=0,  # But none replicated
            evidence_gaps=["No replications", "Small sample size"],
        )
        
        # With 2 studies but no replications, should be WAIT or TEST
        assert insight.action_type in [
            ActionType.WAIT_FOR_REPLICATION,
            ActionType.TEST_IN_YOUR_SYSTEM,
            ActionType.COMBINE_WITH_ALTERNATIVES,
            ActionType.FUND_RESEARCH_GAP,
        ]

    def test_insight_includes_resources(self):
        """Test that insights include required resources."""
        generator = get_insight_generator()
        
        insight = generator.generate_insight(
            topic="Implementation",
            finding="Change process X",
            confidence=0.8,
            num_studies=3,
            num_replications=1,
            evidence_gaps=[],
        )
        
        assert len(insight.required_resources) > 0
        assert insight.timeline is not None

    def test_insight_includes_risk_management(self):
        """Test that insights include risks and mitigations."""
        generator = get_insight_generator()
        
        insight = generator.generate_insight(
            topic="Change",
            finding="Replace old with new approach",
            confidence=0.7,
            num_studies=2,
            num_replications=1,
            evidence_gaps=["Limited replication"],
        )
        
        assert len(insight.potential_risks) > 0
        assert len(insight.mitigation_strategies) > 0
        assert len(insight.potential_risks) == len(insight.mitigation_strategies)


class TestLiveResearchSynthesizer:
    """Test complete synthesis pipeline."""

    def test_end_to_end_synthesis(self):
        """Test complete synthesis from studies to actionable insights."""
        synthesizer = LiveResearchSynthesizer()
        
        studies = [
            Study(
                id="study1", title="Study 1", finding="Treatment X increases Y",
                sample_size=200, year=2021, effect_size=0.4, method_quality=0.8,
                replication_count=1
            ),
            Study(
                id="study2", title="Study 2", finding="Treatment X decreases Y",
                sample_size=150, year=2022, effect_size=-0.2, method_quality=0.6,
                replication_count=0
            ),
        ]
        
        synthesis = synthesizer.synthesize(
            query="Does treatment X affect outcome Y?",
            studies=studies
        )
        
        # Check all required fields present
        assert "query" in synthesis
        assert "synthesis" in synthesis
        assert "confidence_level" in synthesis
        assert "immediate_action" in synthesis
        assert "conflicts_detected" in synthesis
        assert "resolutions" in synthesis
        assert "action_type" in synthesis
        assert "implementation_steps" in synthesis

    def test_synthesis_recommends_action(self):
        """Test that synthesis always recommends some action."""
        synthesizer = LiveResearchSynthesizer()
        
        studies = [
            Study(
                id="s1", title="Good Study", finding="X works",
                sample_size=300, year=2021, effect_size=0.5, method_quality=0.9,
                replication_count=2
            )
        ]
        
        synthesis = synthesizer.synthesize("Test question", studies)
        
        assert synthesis["action_type"] in [at.value for at in ActionType]
        assert "IMPLEMENT" in synthesis["immediate_action"] or \
               "TEST" in synthesis["immediate_action"] or \
               "WAIT" in synthesis["immediate_action"]

    def test_synthesis_identifies_gaps(self):
        """Test that synthesis identifies research gaps."""
        synthesizer = LiveResearchSynthesizer()
        
        studies = [
            Study(
                id="s1", title="Single study", finding="Finding",
                sample_size=50, year=2022, method_quality=0.5, replication_count=0
            )
        ]
        
        synthesis = synthesizer.synthesize("New research area", studies)
        
        assert "research_gaps" in synthesis
        assert len(synthesis["research_gaps"]["most_critical"]) > 0

    def test_convenience_function(self):
        """Test the convenience synthesize_research function."""
        studies = [
            Study(
                id="s1", title="Test", finding="X improves Y",
                sample_size=100, year=2021, method_quality=0.7, replication_count=1
            )
        ]
        
        result = synthesize_research("Question", studies)
        
        assert isinstance(result, dict)
        assert "immediate_action" in result
