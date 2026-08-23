"""
Phase 11: Actionable Insight Generator

Transforms research findings into immediate actions scientists can take.

Solves: "Now that I know this, what do I DO?"
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Types of actions scientists can take."""
    IMPLEMENT_IMMEDIATELY = "implement_immediately"
    TEST_IN_YOUR_SYSTEM = "test_in_your_system"
    WAIT_FOR_REPLICATION = "wait_for_replication"
    COMBINE_WITH_ALTERNATIVES = "combine_with_alternatives"
    MONITOR_FOR_UPDATES = "monitor_for_updates"
    FUND_RESEARCH_GAP = "fund_research_gap"


@dataclass
class Insight:
    """An actionable insight for a scientist."""
    insight_id: str
    topic: str
    finding: str
    confidence: float  # 0-1
    
    action_type: ActionType
    immediate_action: str  # What to do NOW
    
    # Implementation
    implementation_steps: List[str]
    required_resources: List[str]
    timeline: str  # "Days", "Weeks", "Months"
    expected_impact: str
    
    # Risk management
    potential_risks: List[str]
    mitigation_strategies: List[str]
    
    # Future research
    research_gap: str  # What's not known yet?
    research_priority: str  # How urgent?
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InsightBundle:
    """A bundle of related insights from a synthesis."""
    query: str
    num_studies_reviewed: int
    insights: List[Insight]
    consensus_finding: str
    uncertainty_statement: str
    critical_gaps: List[str]


class InsightGenerator:
    """
    Converts research findings into immediate actions.
    
    Scientists NEED this: "Given these papers, what should I actually DO?"
    """

    def __init__(self):
        self.insights: List[Insight] = []

    def generate_insight(
        self,
        topic: str,
        finding: str,
        confidence: float,
        num_studies: int,
        num_replications: int,
        evidence_gaps: List[str],
    ) -> Insight:
        """
        Generate an actionable insight from research findings.
        
        Args:
            topic: Research topic
            finding: Main finding
            confidence: 0-1 confidence level
            num_studies: How many studies support this?
            num_replications: How many replications?
            evidence_gaps: What's not known?
            
        Returns:
            Actionable insight
        """
        
        # Determine action type based on confidence & replication
        action_type = self._determine_action_type(
            confidence, num_replications
        )

        # Generate immediate action
        immediate_action = self._generate_immediate_action(
            finding, confidence, action_type
        )

        # Generate implementation steps
        implementation_steps = self._generate_implementation_steps(
            finding, action_type
        )

        # Identify resources needed
        resources = self._identify_resources(action_type)

        # Identify risks
        risks, mitigations = self._identify_risks(finding, confidence)

        # Identify research gaps
        research_gap = self._prioritize_research_gaps(evidence_gaps)

        insight = Insight(
            insight_id=f"insight_{topic}_{confidence:.0%}",
            topic=topic,
            finding=finding,
            confidence=confidence,
            action_type=action_type,
            immediate_action=immediate_action,
            implementation_steps=implementation_steps,
            required_resources=resources,
            timeline=self._estimate_timeline(action_type),
            expected_impact=self._estimate_impact(confidence),
            potential_risks=risks,
            mitigation_strategies=mitigations,
            research_gap=research_gap,
            research_priority=self._prioritize_research(confidence, num_replications),
        )

        self.insights.append(insight)
        return insight

    def _determine_action_type(
        self, 
        confidence: float,
        replications: int
    ) -> ActionType:
        """Determine what action to take based on evidence."""
        
        if confidence > 0.8 and replications >= 3:
            return ActionType.IMPLEMENT_IMMEDIATELY
        elif confidence > 0.7 and replications >= 2:
            return ActionType.TEST_IN_YOUR_SYSTEM
        elif confidence > 0.6 and replications == 0:
            return ActionType.WAIT_FOR_REPLICATION
        elif confidence > 0.5:
            return ActionType.COMBINE_WITH_ALTERNATIVES
        else:
            return ActionType.FUND_RESEARCH_GAP

    def _generate_immediate_action(
        self,
        finding: str,
        confidence: float,
        action_type: ActionType,
    ) -> str:
        """Generate the immediate action."""
        
        if action_type == ActionType.IMPLEMENT_IMMEDIATELY:
            return (
                f"🚀 IMPLEMENT NOW: {finding} "
                f"(Confidence: {confidence:.0%}). "
                f"This is well-supported and ready for immediate use."
            )
        elif action_type == ActionType.TEST_IN_YOUR_SYSTEM:
            return (
                f"🧪 TEST IT: {finding} "
                f"(Confidence: {confidence:.0%}). "
                f"Run a small pilot in your system to validate before full implementation."
            )
        elif action_type == ActionType.WAIT_FOR_REPLICATION:
            return (
                f"⏳ WAIT: The finding '{finding}' "
                f"(Confidence: {confidence:.0%}) has not been replicated yet. "
                f"Wait for replication before implementing."
            )
        elif action_type == ActionType.COMBINE_WITH_ALTERNATIVES:
            return (
                f"🔀 COMBINE: Use '{finding}' alongside existing methods "
                f"(Confidence: {confidence:.0%}). Don't replace entirely yet."
            )
        elif action_type == ActionType.MONITOR_FOR_UPDATES:
            return (
                f"📊 MONITOR: The evidence for '{finding}' "
                f"(Confidence: {confidence:.0%}) is evolving. Stay informed."
            )
        else:  # FUND_RESEARCH_GAP
            return (
                f"💡 RESEARCH OPPORTUNITY: This area ('{finding}') is understudied "
                f"(Confidence: {confidence:.0%}). Consider funding research here."
            )

    def _generate_implementation_steps(
        self,
        finding: str,
        action_type: ActionType,
    ) -> List[str]:
        """Generate step-by-step implementation instructions."""
        
        if action_type == ActionType.IMPLEMENT_IMMEDIATELY:
            return [
                "1. Review the full evidence (3+ studies, 2+ replications)",
                "2. Prepare your team/system for the change",
                "3. Implement the recommendation fully",
                "4. Monitor outcomes for 3-6 months",
                "5. Report results back to the research community",
            ]
        elif action_type == ActionType.TEST_IN_YOUR_SYSTEM:
            return [
                "1. Define a pilot group (10-20% of usual scope)",
                "2. Run controlled test: treatment vs control",
                "3. Measure outcomes carefully for 4-8 weeks",
                "4. Compare results to historical baseline",
                "5. If positive, scale up; if negative, stick with current approach",
            ]
        elif action_type == ActionType.WAIT_FOR_REPLICATION:
            return [
                "1. Save the original study for reference",
                "2. Set a reminder to check for replications in 1-2 years",
                "3. Follow the original authors' future work",
                "4. Subscribe to alerts for related research",
                "5. When replication appears, revisit the decision",
            ]
        elif action_type == ActionType.COMBINE_WITH_ALTERNATIVES:
            return [
                "1. Keep your current approach as baseline",
                "2. Add the new finding as a complementary strategy",
                "3. Test synergies between old + new approach",
                "4. Measure whether combination outperforms either alone",
                "5. Gradually increase reliance on new finding if synergies confirmed",
            ]
        else:
            return [
                "1. Identify the key research questions",
                "2. Design a study to answer them",
                "3. Secure funding",
                "4. Conduct the research",
                "5. Publish results to advance the field",
            ]

    def _identify_resources(self, action_type: ActionType) -> List[str]:
        """Identify resources needed."""
        
        if action_type == ActionType.IMPLEMENT_IMMEDIATELY:
            return [
                "Staff training (1-2 days)",
                "Equipment/software upgrades (if any)",
                "Budget for implementation (varies)",
                "Monitoring systems",
            ]
        elif action_type == ActionType.TEST_IN_YOUR_SYSTEM:
            return [
                "Pilot group (10-20% of normal volume)",
                "Control group (same size)",
                "Measurement/monitoring systems",
                "Data analysis capability",
                "Staff time (2-4 hours/week for 4-8 weeks)",
            ]
        elif action_type == ActionType.WAIT_FOR_REPLICATION:
            return [
                "Literature monitoring service or saved search",
                "Calendar reminder system",
                "Once/year review time (1 hour)",
            ]
        else:
            return [
                "Research funding (varies by field)",
                "Study design consultation",
                "Subject recruitment (if applicable)",
                "Data collection infrastructure",
            ]

    def _estimate_timeline(self, action_type: ActionType) -> str:
        """Estimate timeline to results."""
        
        timelines = {
            ActionType.IMPLEMENT_IMMEDIATELY: "Days (implementation) + weeks (outcome measurement)",
            ActionType.TEST_IN_YOUR_SYSTEM: "4-8 weeks (pilot)",
            ActionType.WAIT_FOR_REPLICATION: "1-3 years (waiting) + days (decision review)",
            ActionType.COMBINE_WITH_ALTERNATIVES: "Weeks to months (testing synergies)",
            ActionType.MONITOR_FOR_UPDATES: "Ongoing (1 hour/year)",
            ActionType.FUND_RESEARCH_GAP: "1-3 years (research cycle)",
        }
        return timelines.get(action_type, "Unknown")

    def _estimate_impact(self, confidence: float) -> str:
        """Estimate potential impact."""
        
        if confidence > 0.8:
            return "HIGH: Well-supported by evidence"
        elif confidence > 0.6:
            return "MODERATE: Reasonably supported"
        elif confidence > 0.4:
            return "LOW: Weakly supported - test first"
        else:
            return "UNCERTAIN: More research needed"

    def _identify_risks(
        self, 
        finding: str,
        confidence: float
    ) -> tuple[List[str], List[str]]:
        """Identify risks and mitigations."""
        
        risks = []
        mitigations = []

        if confidence < 0.7:
            risks.append("Finding may not replicate in your context")
            mitigations.append("Run controlled pilot test first")

        if "expensive" in finding.lower() or "costly" in finding.lower():
            risks.append("Implementation cost")
            mitigations.append("Start with pilot to validate ROI")

        if "new" in finding.lower():
            risks.append("Staff learning curve")
            mitigations.append("Provide training and support")

        if "replaces" in finding.lower():
            risks.append("Disruption to current workflow")
            mitigations.append("Gradual rollout instead of immediate replacement")

        # Generic risks
        if not risks:
            risks = ["General uncertainty in real-world application"]
            mitigations = ["Monitor outcomes closely during implementation"]

        return risks, mitigations

    def _prioritize_research_gaps(self, gaps: List[str]) -> str:
        """Prioritize research gaps."""
        
        if not gaps:
            return "No major gaps identified - this finding is well-understood."
        
        # Return the most critical gap
        return gaps[0]

    def _prioritize_research(
        self, 
        confidence: float,
        replications: int
    ) -> str:
        """Prioritize future research."""
        
        if confidence < 0.4 and replications == 0:
            return "CRITICAL PRIORITY: Urgent research needed"
        elif confidence < 0.6 and replications < 2:
            return "HIGH PRIORITY: Research needed soon"
        elif confidence < 0.8 and replications < 3:
            return "MEDIUM PRIORITY: Additional replications helpful"
        else:
            return "LOW PRIORITY: Evidence is solid, incremental improvements only"

    def generate_insight_bundle(
        self,
        query: str,
        num_studies: int,
        insights: List[Insight],
        consensus: str,
        uncertainty: str,
        gaps: List[str],
    ) -> InsightBundle:
        """Bundle multiple insights from a research synthesis."""
        
        bundle = InsightBundle(
            query=query,
            num_studies_reviewed=num_studies,
            insights=insights,
            consensus_finding=consensus,
            uncertainty_statement=uncertainty,
            critical_gaps=gaps,
        )

        logger.info(
            f"Generated insight bundle for '{query}': "
            f"{len(insights)} insights, {len(gaps)} research gaps"
        )

        return bundle


def get_insight_generator() -> InsightGenerator:
    """Get an insight generator instance."""
    return InsightGenerator()
