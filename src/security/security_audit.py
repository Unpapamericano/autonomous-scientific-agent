"""
Phase 8: Security Audit Logging

Logs all security-relevant events for compliance and debugging:
  - Injection detection attempts
  - Sanitization actions
  - Code execution events
  - Tool access
  - API calls
  - Error/exception events
"""

import logging
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any, Optional, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityEventType(str, Enum):
    """Type of security event."""
    INJECTION_DETECTED = "injection_detected"
    SANITIZATION_APPLIED = "sanitization_applied"
    CODE_EXECUTION = "code_execution"
    TOOL_ACCESS = "tool_access"
    API_CALL = "api_call"
    ERROR = "error"
    WARNING = "warning"
    ACCESS_DENIED = "access_denied"


@dataclass
class SecurityEvent:
    """A security-relevant event."""
    event_type: SecurityEventType
    timestamp: str
    severity: str  # "info", "warning", "critical"
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}

    def to_json(self) -> str:
        """Convert to JSON for logging."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        return json.dumps(data)


class SecurityAuditLogger:
    """
    Logs security events for compliance and debugging.
    """

    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.events = []

    def log_injection_detected(
        self,
        injection_type: str,
        severity: str,
        confidence: float,
        patterns: list,
        input_sample: str = None,
    ):
        """Log injection detection."""
        event = SecurityEvent(
            event_type=SecurityEventType.INJECTION_DETECTED,
            timestamp=datetime.utcnow().isoformat(),
            severity=severity,
            message=f"Injection detected: {injection_type}",
            user_id=self.user_id,
            session_id=self.session_id,
            details={
                "injection_type": injection_type,
                "confidence": confidence,
                "patterns_detected": patterns,
                "input_sample": input_sample[:100] if input_sample else None,
            },
        )
        self.events.append(event)
        logger.warning(event.to_json())

    def log_sanitization(
        self,
        action: str,
        original_length: int,
        sanitized_length: int,
        changes_made: list,
    ):
        """Log sanitization action."""
        event = SecurityEvent(
            event_type=SecurityEventType.SANITIZATION_APPLIED,
            timestamp=datetime.utcnow().isoformat(),
            severity="info",
            message=f"Sanitization applied: {action}",
            user_id=self.user_id,
            session_id=self.session_id,
            details={
                "action": action,
                "original_length": original_length,
                "sanitized_length": sanitized_length,
                "changes": changes_made,
            },
        )
        self.events.append(event)
        logger.info(event.to_json())

    def log_code_execution(
        self,
        code_hash: str,
        language: str,
        timeout_seconds: int,
        success: bool,
        error: str = None,
    ):
        """Log code execution."""
        event = SecurityEvent(
            event_type=SecurityEventType.CODE_EXECUTION,
            timestamp=datetime.utcnow().isoformat(),
            severity="critical" if not success else "info",
            message=f"Code execution: {language} (success={success})",
            user_id=self.user_id,
            session_id=self.session_id,
            details={
                "code_hash": code_hash,
                "language": language,
                "timeout_seconds": timeout_seconds,
                "success": success,
                "error": error,
            },
        )
        self.events.append(event)
        logger.warning(event.to_json()) if not success else logger.info(event.to_json())

    def log_tool_access(
        self,
        tool_name: str,
        parameters_hash: str,
        success: bool,
        error: str = None,
    ):
        """Log tool access."""
        event = SecurityEvent(
            event_type=SecurityEventType.TOOL_ACCESS,
            timestamp=datetime.utcnow().isoformat(),
            severity="info",
            message=f"Tool accessed: {tool_name}",
            user_id=self.user_id,
            session_id=self.session_id,
            details={
                "tool_name": tool_name,
                "parameters_hash": parameters_hash,
                "success": success,
                "error": error,
            },
        )
        self.events.append(event)
        logger.info(event.to_json())

    def log_access_denied(
        self,
        reason: str,
        resource: str,
        user_id: str = None,
    ):
        """Log access denial."""
        event = SecurityEvent(
            event_type=SecurityEventType.ACCESS_DENIED,
            timestamp=datetime.utcnow().isoformat(),
            severity="warning",
            message=f"Access denied: {reason}",
            user_id=user_id or self.user_id,
            session_id=self.session_id,
            details={
                "reason": reason,
                "resource": resource,
            },
        )
        self.events.append(event)
        logger.warning(event.to_json())

    def get_event_summary(self) -> Dict[str, Any]:
        """Get summary of logged events."""
        return {
            "total_events": len(self.events),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "events": [asdict(e) for e in self.events],
        }
