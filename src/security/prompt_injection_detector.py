"""
Phase 8: Prompt Injection Detection

Detects common prompt injection attacks:
  - Prompt override attempts (e.g., "Ignore previous instructions...")
  - Token smuggling (hidden instructions in quoted/encoded strings)
  - Role confusion (e.g., "You are now a hacker...")
  - Jailbreak patterns (e.g., "I'm testing your security...")
  - Command injection (SQL, shell, code patterns)
  - Data exfiltration (requests for internal state/credentials)

Uses heuristic patterns + keyword detection (Phase 8).
Phase 9+ could add ML-based detection.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

# Severity comparison helper
_SEVERITY_RANK = {"safe": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


class InjectionSeverity(str, Enum):
    """Severity level of detected injection."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __lt__(self, other):
        if not isinstance(other, InjectionSeverity):
            return NotImplemented
        return _SEVERITY_RANK[self.value] < _SEVERITY_RANK[other.value]

    def __le__(self, other):
        if not isinstance(other, InjectionSeverity):
            return NotImplemented
        return _SEVERITY_RANK[self.value] <= _SEVERITY_RANK[other.value]

    def __gt__(self, other):
        if not isinstance(other, InjectionSeverity):
            return NotImplemented
        return _SEVERITY_RANK[self.value] > _SEVERITY_RANK[other.value]

    def __ge__(self, other):
        if not isinstance(other, InjectionSeverity):
            return NotImplemented
        return _SEVERITY_RANK[self.value] >= _SEVERITY_RANK[other.value]


class InjectionType(str, Enum):
    """Type of injection detected."""
    NONE = "none"
    PROMPT_OVERRIDE = "prompt_override"
    ROLE_CONFUSION = "role_confusion"
    JAILBREAK = "jailbreak"
    COMMAND_INJECTION = "command_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    TOKEN_SMUGGLING = "token_smuggling"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"


@dataclass
class InjectionResult:
    """Result of prompt injection detection."""
    is_malicious: bool
    injection_type: InjectionType
    severity: InjectionSeverity
    confidence: float  # 0.0-1.0
    detected_patterns: List[str]
    explanation: str
    suggested_action: str  # block, warn, proceed


class PromptInjectionDetector:
    """
    Detects prompt injection attacks in user inputs.
    """

    # Pattern definitions
    OVERRIDE_PATTERNS = [
        r"ignore\s+(?:previous|earlier|prior|my)\s+(?:instructions|request|message)",
        r"forget\s+(?:previous|earlier|prior|my|the)\s+(?:instructions|request)",
        r"disregard\s+(?:previous|earlier|prior)",
        r"(?:start|begin)\s+(?:new|fresh)\s+(?:conversation|chat|task)",
        r"(?:override|bypass|skip)\s+(?:the\s+)?(?:safety|security|guard)",
    ]

    ROLE_CONFUSION_PATTERNS = [
        r"you\s+(?:are\s+)?(?:now|become|act\s+as)\s+(?:a\s+)?(?:hacker|admin|malicious|evil)",
        r"(?:pretend|roleplay|imagine)\s+you\s+(?:are|were|could be)\s+(?:not\s+)?a\s+(?:safety|security|moderation)",
        r"assume\s+the\s+role\s+of\s+(?:system|admin|root)",
    ]

    JAILBREAK_PATTERNS = [
        r"(?:i'm|i am)\s+(?:just\s+)?testing\s+(?:your|the)\s+(?:security|safety|limits)",
        r"this\s+is\s+(?:just\s+)?a\s+(?:test|game|hypothetical|thought\s+experiment)",
        r"for\s+(?:research|educational|security|ethical\s+)?(?:purposes?|reasons?)",
        r"dev\s+mode",
        r"(?:unlock|enable|activate)\s+(?:dev\s+)?mode",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"(?:drop|delete|truncate)\s+(?:table|database)",  # SQL
        r"(?:rm|rm\s+-rf|del|rmdir)",  # Shell
        r"(?:import\s+os|import\s+sys|from\s+os\s+import)",  # Python escapes
        r"(?:eval|exec|__import__)",  # Code execution
        r"<script|javascript:|onerror=",  # XSS
    ]

    DATA_EXFILTRATION_PATTERNS = [
        r"(?:show|list|give\s+me|return|output)\s+(?:your|the|my)\s+(?:system\s+)?prompt",
        r"(?:what\s+is|reveal)\s+(?:your|the|my)\s+(?:system\s+)?message",
        r"(?:display|expose)\s+(?:your|the)\s+(?:instructions|configuration|settings)",
        r"(?:retrieve|extract|dump)\s+(?:api|key|token|credential|password)",
        r"internal\s+(?:state|memory|context|system)",
    ]

    TOKEN_SMUGGLING_PATTERNS = [
        r'[\'"][^"\']*(?:system|instruction|ignore|override)[^"\']*[\'"]',
        r"\b(?:base64|hex|utf-?8)\s+(?:encoded|decode|encoded\s+as)",
        r"(?:hidden|invisible|zero-?width)\s+(?:instruction|command|text)",
    ]

    def __init__(self, sensitivity: str = "medium"):
        """
        Initialize detector.

        Args:
            sensitivity: "low", "medium" (default), or "high"
                        Higher = more false positives but catches more attacks
        """
        self.sensitivity = sensitivity
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.override_patterns = [re.compile(p, re.IGNORECASE) for p in self.OVERRIDE_PATTERNS]
        self.role_confusion_patterns = [re.compile(p, re.IGNORECASE) for p in self.ROLE_CONFUSION_PATTERNS]
        self.jailbreak_patterns = [re.compile(p, re.IGNORECASE) for p in self.JAILBREAK_PATTERNS]
        self.command_injection_patterns = [re.compile(p, re.IGNORECASE) for p in self.COMMAND_INJECTION_PATTERNS]
        self.data_exfiltration_patterns = [re.compile(p, re.IGNORECASE) for p in self.DATA_EXFILTRATION_PATTERNS]
        self.token_smuggling_patterns = [re.compile(p, re.IGNORECASE) for p in self.TOKEN_SMUGGLING_PATTERNS]

    def detect(self, user_input: str) -> InjectionResult:
        """
        Detect prompt injection attempts in user input.

        Args:
            user_input: User's input text

        Returns:
            InjectionResult with detection status
        """
        if not user_input or len(user_input.strip()) == 0:
            return InjectionResult(
                is_malicious=False,
                injection_type=InjectionType.NONE,
                severity=InjectionSeverity.SAFE,
                confidence=1.0,
                detected_patterns=[],
                explanation="Empty input",
                suggested_action="proceed",
            )

        detected_patterns = []
        injection_type = InjectionType.NONE
        max_severity = InjectionSeverity.SAFE
        confidence = 0.0

        # Check each category
        result = self._check_override(user_input)
        if result["detected"]:
            detected_patterns.extend(result["patterns"])
            injection_type = InjectionType.PROMPT_OVERRIDE
            max_severity = result["severity"] if result["severity"] > max_severity else max_severity
            confidence = max(confidence, result["confidence"])

        result = self._check_role_confusion(user_input)
        if result["detected"]:
            detected_patterns.extend(result["patterns"])
            if result["severity"] > max_severity:
                injection_type = InjectionType.ROLE_CONFUSION
                max_severity = result["severity"]
            confidence = max(confidence, result["confidence"])

        result = self._check_jailbreak(user_input)
        if result["detected"]:
            detected_patterns.extend(result["patterns"])
            if result["severity"] > max_severity:
                injection_type = InjectionType.JAILBREAK
                max_severity = result["severity"]
            confidence = max(confidence, result["confidence"])

        result = self._check_command_injection(user_input)
        if result["detected"]:
            detected_patterns.extend(result["patterns"])
            if result["severity"] > max_severity:
                injection_type = InjectionType.COMMAND_INJECTION
                max_severity = result["severity"]
            confidence = max(confidence, result["confidence"])

        result = self._check_data_exfiltration(user_input)
        if result["detected"]:
            detected_patterns.extend(result["patterns"])
            if result["severity"] > max_severity:
                injection_type = InjectionType.DATA_EXFILTRATION
                max_severity = result["severity"]
            confidence = max(confidence, result["confidence"])

        result = self._check_token_smuggling(user_input)
        if result["detected"]:
            detected_patterns.extend(result["patterns"])
            if result["severity"] > max_severity:
                injection_type = InjectionType.TOKEN_SMUGGLING
                max_severity = result["severity"]
            confidence = max(confidence, result["confidence"])

        # Determine if truly malicious (CRITICAL or HIGH severity)
        is_malicious = max_severity in [InjectionSeverity.HIGH, InjectionSeverity.CRITICAL]

        # Determine suggested action
        if max_severity in [InjectionSeverity.HIGH, InjectionSeverity.CRITICAL]:
            suggested_action = "block"
            explanation = f"Detected {injection_type.value} attack (confidence: {confidence:.2f})"
        elif max_severity == InjectionSeverity.MEDIUM:
            suggested_action = "warn"
            explanation = f"Suspicious patterns detected: {', '.join(detected_patterns[:3])}"
        else:
            suggested_action = "proceed"
            explanation = "No injection detected"

        logger.info(
            f"Injection check: {injection_type.value} (severity={max_severity.value}, "
            f"confidence={confidence:.2f})"
        )

        return InjectionResult(
            is_malicious=is_malicious,
            injection_type=injection_type,
            severity=max_severity,
            confidence=confidence,
            detected_patterns=list(set(detected_patterns)),  # Deduplicate
            explanation=explanation,
            suggested_action=suggested_action,
        )

    def _check_override(self, text: str) -> Dict[str, Any]:
        """Check for prompt override patterns."""
        for pattern in self.override_patterns:
            if pattern.search(text):
                return {
                    "detected": True,
                    "patterns": ["prompt_override"],
                    "severity": InjectionSeverity.CRITICAL,
                    "confidence": 0.95,
                }

        return {"detected": False, "patterns": [], "severity": InjectionSeverity.SAFE, "confidence": 0.0}

    def _check_role_confusion(self, text: str) -> Dict[str, Any]:
        """Check for role confusion patterns."""
        for pattern in self.role_confusion_patterns:
            if pattern.search(text):
                return {
                    "detected": True,
                    "patterns": ["role_confusion"],
                    "severity": InjectionSeverity.HIGH,
                    "confidence": 0.85,
                }

        return {"detected": False, "patterns": [], "severity": InjectionSeverity.SAFE, "confidence": 0.0}

    def _check_jailbreak(self, text: str) -> Dict[str, Any]:
        """Check for jailbreak attempts."""
        for pattern in self.jailbreak_patterns:
            if pattern.search(text):
                return {
                    "detected": True,
                    "patterns": ["jailbreak"],
                    "severity": InjectionSeverity.MEDIUM,
                    "confidence": 0.75,
                }

        return {"detected": False, "patterns": [], "severity": InjectionSeverity.SAFE, "confidence": 0.0}

    def _check_command_injection(self, text: str) -> Dict[str, Any]:
        """Check for command injection patterns."""
        for pattern in self.command_injection_patterns:
            if pattern.search(text):
                return {
                    "detected": True,
                    "patterns": ["command_injection"],
                    "severity": InjectionSeverity.CRITICAL,
                    "confidence": 0.90,
                }

        return {"detected": False, "patterns": [], "severity": InjectionSeverity.SAFE, "confidence": 0.0}

    def _check_data_exfiltration(self, text: str) -> Dict[str, Any]:
        """Check for data exfiltration attempts."""
        for pattern in self.data_exfiltration_patterns:
            if pattern.search(text):
                return {
                    "detected": True,
                    "patterns": ["data_exfiltration"],
                    "severity": InjectionSeverity.HIGH,
                    "confidence": 0.80,
                }

        return {"detected": False, "patterns": [], "severity": InjectionSeverity.SAFE, "confidence": 0.0}

    def _check_token_smuggling(self, text: str) -> Dict[str, Any]:
        """Check for token smuggling patterns."""
        for pattern in self.token_smuggling_patterns:
            if pattern.search(text):
                return {
                    "detected": True,
                    "patterns": ["token_smuggling"],
                    "severity": InjectionSeverity.MEDIUM,
                    "confidence": 0.65,
                }

        return {"detected": False, "patterns": [], "severity": InjectionSeverity.SAFE, "confidence": 0.0}


def get_injection_detector(sensitivity: str = "medium") -> PromptInjectionDetector:
    """Get a prompt injection detector instance."""
    return PromptInjectionDetector(sensitivity=sensitivity)
