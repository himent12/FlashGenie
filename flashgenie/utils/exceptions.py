"""
Custom exceptions for FlashGenie.

This module defines all custom exceptions used throughout
the FlashGenie application for better error handling.
"""


class FlashGenieError(Exception):
    """Base exception for all FlashGenie-specific errors."""
    pass


class ValidationError(FlashGenieError):
    """Raised when data validation fails."""
    pass


class ImportError(FlashGenieError):
    """Raised when file import operations fail."""
    pass


class ExportError(FlashGenieError):
    """Raised when file export operations fail."""
    pass


class StorageError(FlashGenieError):
    """Raised when data storage operations fail."""
    pass


class QuizError(FlashGenieError):
    """Raised when quiz operations fail."""
    pass


class ConfigurationError(FlashGenieError):
    """Raised when configuration is invalid."""
    pass


class DeckNotFoundError(StorageError):
    """Raised when a requested deck cannot be found."""
    pass


class FlashcardNotFoundError(StorageError):
    """Raised when a requested flashcard cannot be found."""
    pass


class UnsupportedFormatError(ImportError):
    """Raised when trying to import an unsupported file format."""
    pass


class CorruptedDataError(StorageError):
    """Raised when stored data is corrupted or invalid."""
    pass


class PluginError(FlashGenieError):
    """Raised when plugin operations fail."""
    pass


class ContextAnalysisError(FlashGenieError):
    """Raised when context analysis operations fail."""
    pass


class PatternAnalysisError(FlashGenieError):
    """Raised when pattern analysis operations fail."""
    pass


class InsightGenerationError(FlashGenieError):
    """Raised when insight generation operations fail."""
    pass


class SecurityError(FlashGenieError):
    """Raised when security violations are detected."""
    pass


class PermissionError(FlashGenieError):
    """Raised when permission checks fail."""
    pass
