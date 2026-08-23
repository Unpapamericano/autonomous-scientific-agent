"""
Phase 8: Input Sanitization

Cleans and validates user inputs before processing:
  - Remove/normalize whitespace
  - Escape special characters
  - Truncate to max length
  - Validate character sets
  - Remove suspicious patterns
  - Normalize encodings
"""

import logging
import re
import unicodedata
from typing import Optional

logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Sanitizes user inputs for safety and consistency.
    """

    def __init__(
        self,
        max_length: int = 5000,
        allow_special_chars: bool = True,
        normalize_unicode: bool = True,
    ):
        """
        Initialize sanitizer.

        Args:
            max_length: Maximum input length
            allow_special_chars: Allow !@#$%^&*() etc.
            normalize_unicode: Normalize Unicode (NFD/NFC)
        """
        self.max_length = max_length
        self.allow_special_chars = allow_special_chars
        self.normalize_unicode = normalize_unicode

    def sanitize(self, text: str) -> str:
        """
        Sanitize input text.

        Args:
            text: Raw input

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # 1. Normalize Unicode
        if self.normalize_unicode:
            text = unicodedata.normalize("NFKD", text)

        # 2. Remove null bytes and control characters
        text = "".join(ch for ch in text if ch == "\n" or not unicodedata.category(ch).startswith("C"))

        # 3. Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        # 4. Truncate to max length
        if len(text) > self.max_length:
            logger.warning(f"Input truncated from {len(text)} to {self.max_length} chars")
            text = text[: self.max_length]

        # 5. Remove suspicious patterns (common injection attempts)
        text = self._remove_suspicious_patterns(text)

        return text

    def _remove_suspicious_patterns(self, text: str) -> str:
        """Remove known malicious patterns."""
        suspicious = [
            r"<script[^>]*>.*?</script>",  # JavaScript
            r"javascript:",  # Protocol
            r"onerror\s*=",  # Event handler
            r"onclick\s*=",  # Event handler
        ]

        for pattern in suspicious:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

        return text

    def sanitize_code(self, code: str) -> str:
        """
        Sanitize Python code before execution.

        Args:
            code: Python code string

        Returns:
            Sanitized code
        """
        if not code:
            return ""

        # 1. Remove null bytes
        code = code.replace("\0", "")

        # 2. Block dangerous imports
        dangerous_imports = [
            "import os",
            "import sys",
            "import subprocess",
            "import socket",
            "import urllib",
            "import requests",
            "from os import",
            "from sys import",
            "__import__",
            "exec(",
            "eval(",
            "open(",
        ]

        for dangerous in dangerous_imports:
            if dangerous.lower() in code.lower():
                logger.error(f"Dangerous pattern detected in code: {dangerous}")
                raise ValueError(f"Code contains blocked pattern: {dangerous}")

        # 3. Truncate
        if len(code) > self.max_length:
            raise ValueError(f"Code exceeds max length ({self.max_length})")

        return code


def get_sanitizer(max_length: int = 5000) -> InputSanitizer:
    """Get an input sanitizer instance."""
    return InputSanitizer(max_length=max_length)
