"""
Security utilities for FlashGenie.

This module provides security-related functions including input validation,
sanitization, and security checks.
"""

import re
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

from .exceptions import SecurityError, ValidationError


class SecurityValidator:
    """Provides security validation and sanitization functions."""
    
    def __init__(self):
        """Initialize the security validator."""
        self.logger = logging.getLogger(__name__)
        
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
            r'subprocess\.',
            r'os\.system',
            r'os\.popen',
            r'os\.spawn',
            r'pickle\.loads',
            r'marshal\.loads',
            r'shelve\.',
        ]
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.*set',
            r'alter\s+table',
            r'create\s+table',
            r'--\s*$',
            r'/\*.*\*/',
            r';\s*--',
            r';\s*/\*',
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>',
            r'</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
        ]
    
    def validate_input(self, value: Any, input_type: str, **kwargs) -> Any:
        """
        Validate and sanitize input based on type.
        
        Args:
            value: Input value to validate
            input_type: Type of input (string, filename, path, etc.)
            **kwargs: Additional validation parameters
            
        Returns:
            Validated and sanitized value
            
        Raises:
            ValidationError: If validation fails
            SecurityError: If security issues are detected
        """
        if value is None:
            if kwargs.get('required', False):
                raise ValidationError(f"Required {input_type} cannot be None")
            return value
        
        if input_type == 'string':
            return self._validate_string(value, **kwargs)
        elif input_type == 'filename':
            return self._validate_filename(value, **kwargs)
        elif input_type == 'path':
            return self._validate_path(value, **kwargs)
        elif input_type == 'email':
            return self._validate_email(value, **kwargs)
        elif input_type == 'url':
            return self._validate_url(value, **kwargs)
        elif input_type == 'code':
            return self._validate_code(value, **kwargs)
        else:
            raise ValidationError(f"Unknown input type: {input_type}")
    
    def _validate_string(self, value: str, **kwargs) -> str:
        """Validate string input."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        
        # Check length limits
        max_length = kwargs.get('max_length', 10000)
        min_length = kwargs.get('min_length', 0)
        
        if len(value) > max_length:
            raise ValidationError(f"String too long (max {max_length} characters)")
        
        if len(value) < min_length:
            raise ValidationError(f"String too short (min {min_length} characters)")
        
        # Check for dangerous patterns
        if kwargs.get('check_dangerous', True):
            self._check_dangerous_patterns(value)
        
        # Check for XSS patterns
        if kwargs.get('check_xss', True):
            self._check_xss_patterns(value)
        
        # Sanitize if requested
        if kwargs.get('sanitize', False):
            value = self._sanitize_string(value)
        
        return value
    
    def _validate_filename(self, value: str, **kwargs) -> str:
        """Validate filename input."""
        if not isinstance(value, str):
            raise ValidationError("Filename must be a string")
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_chars:
            if char in value:
                raise SecurityError(f"Dangerous character '{char}' in filename")
        
        # Check for path traversal
        if '..' in value or value.startswith('/') or value.startswith('\\'):
            raise SecurityError("Path traversal attempt detected in filename")
        
        # Check length
        if len(value) > 255:
            raise ValidationError("Filename too long (max 255 characters)")
        
        if not value.strip():
            raise ValidationError("Filename cannot be empty")
        
        return value.strip()
    
    def _validate_path(self, value: Union[str, Path], **kwargs) -> Path:
        """Validate path input."""
        if isinstance(value, str):
            path = Path(value)
        elif isinstance(value, Path):
            path = value
        else:
            raise ValidationError("Path must be a string or Path object")
        
        # Convert to absolute path for security checks
        try:
            abs_path = path.resolve()
        except Exception as e:
            raise ValidationError(f"Invalid path: {e}")
        
        # Check if path is within allowed directories
        allowed_dirs = kwargs.get('allowed_dirs', [])
        if allowed_dirs:
            allowed = False
            for allowed_dir in allowed_dirs:
                try:
                    abs_path.relative_to(Path(allowed_dir).resolve())
                    allowed = True
                    break
                except ValueError:
                    continue
            
            if not allowed:
                raise SecurityError("Path outside allowed directories")
        
        return abs_path
    
    def _validate_email(self, value: str, **kwargs) -> str:
        """Validate email input."""
        if not isinstance(value, str):
            raise ValidationError("Email must be a string")
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError("Invalid email format")
        
        return value.lower().strip()
    
    def _validate_url(self, value: str, **kwargs) -> str:
        """Validate URL input."""
        if not isinstance(value, str):
            raise ValidationError("URL must be a string")
        
        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, value, re.IGNORECASE):
            raise ValidationError("Invalid URL format")
        
        # Check for dangerous schemes
        dangerous_schemes = ['javascript:', 'vbscript:', 'data:', 'file:']
        for scheme in dangerous_schemes:
            if value.lower().startswith(scheme):
                raise SecurityError(f"Dangerous URL scheme: {scheme}")
        
        return value.strip()
    
    def _validate_code(self, value: str, **kwargs) -> str:
        """Validate code input for dangerous patterns."""
        if not isinstance(value, str):
            raise ValidationError("Code must be a string")
        
        # Always check for dangerous patterns in code
        self._check_dangerous_patterns(value)
        
        # Check for specific code patterns
        if 'import os' in value or 'import sys' in value:
            if not kwargs.get('allow_system_imports', False):
                raise SecurityError("System imports not allowed")
        
        return value
    
    def _check_dangerous_patterns(self, value: str) -> None:
        """Check for dangerous code patterns."""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
    
    def _check_xss_patterns(self, value: str) -> None:
        """Check for XSS patterns."""
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(f"Potential XSS pattern detected: {pattern}")
    
    def _check_sql_injection_patterns(self, value: str) -> None:
        """Check for SQL injection patterns."""
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(f"Potential SQL injection pattern detected: {pattern}")
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string by removing/escaping dangerous characters."""
        # Remove null bytes
        value = value.replace('\0', '')
        
        # Escape HTML entities
        html_escape_table = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
        }
        
        for char, escape in html_escape_table.items():
            value = value.replace(char, escape)
        
        return value
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.
        
        Args:
            length: Length of the token in bytes
            
        Returns:
            Secure random token as hex string
        """
        return secrets.token_hex(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """
        Hash a password with salt.
        
        Args:
            password: Password to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA-256
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed.hex(), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hashed_password: Stored hash
            salt: Salt used for hashing
            
        Returns:
            True if password matches
        """
        computed_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, hashed_password)
    
    def sanitize_for_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize data for safe logging by removing sensitive information.
        
        Args:
            data: Data dictionary to sanitize
            
        Returns:
            Sanitized data dictionary
        """
        sensitive_keys = [
            'password', 'token', 'secret', 'key', 'api_key',
            'auth', 'credential', 'private', 'confidential'
        ]
        
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if key contains sensitive information
            is_sensitive = any(sensitive in key_lower for sensitive in sensitive_keys)
            
            if is_sensitive:
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_for_logging(value)
            elif isinstance(value, str) and len(value) > 100:
                # Truncate very long strings
                sanitized[key] = value[:100] + '...'
            else:
                sanitized[key] = value
        
        return sanitized


# Global security validator instance
security_validator = SecurityValidator()


def validate_input(value: Any, input_type: str, **kwargs) -> Any:
    """Convenience function for input validation."""
    return security_validator.validate_input(value, input_type, **kwargs)


def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for logging sanitization."""
    return security_validator.sanitize_for_logging(data)
