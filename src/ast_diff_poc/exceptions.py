"""Custom exceptions for AST Diff POC."""

from typing import Optional


class ASTDiffException(Exception):
    """Base exception for all AST Diff related errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize the exception.
        
        Args:
            message: Error message.
            details: Additional error details.
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class ParsingException(ASTDiffException):
    """Exception raised when property file parsing fails."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, line_number: Optional[int] = None):
        """Initialize parsing exception.
        
        Args:
            message: Error message.
            file_path: Path to the file that failed to parse.
            line_number: Line number where parsing failed.
        """
        self.file_path = file_path
        self.line_number = line_number
        details = f"File: {file_path}" if file_path else None
        if line_number:
            details = f"{details}, Line: {line_number}" if details else f"Line: {line_number}"
        super().__init__(message, details)


class DiffCalculationException(ASTDiffException):
    """Exception raised when diff calculation fails."""
    
    def __init__(self, message: str, source_file: Optional[str] = None, target_file: Optional[str] = None):
        """Initialize diff calculation exception.
        
        Args:
            message: Error message.
            source_file: Source file path.
            target_file: Target file path.
        """
        self.source_file = source_file
        self.target_file = target_file
        details = None
        if source_file or target_file:
            details = f"Source: {source_file}, Target: {target_file}" if source_file and target_file else f"File: {source_file or target_file}"
        super().__init__(message, details)


class ComplexityCalculationException(ASTDiffException):
    """Exception raised when complexity calculation fails."""
    
    def __init__(self, message: str, change_key: Optional[str] = None):
        """Initialize complexity calculation exception.
        
        Args:
            message: Error message.
            change_key: Key of the change that failed.
        """
        self.change_key = change_key
        details = f"Change key: {change_key}" if change_key else None
        super().__init__(message, details)


class TokenizationException(ASTDiffException):
    """Exception raised when tokenization fails."""
    
    def __init__(self, message: str, value: Optional[str] = None):
        """Initialize tokenization exception.
        
        Args:
            message: Error message.
            value: Value that failed to tokenize.
        """
        self.value = value
        details = f"Value: {value[:50]}..." if value and len(value) > 50 else f"Value: {value}" if value else None
        super().__init__(message, details)


class NormalizationException(ASTDiffException):
    """Exception raised when AST normalization fails."""
    
    def __init__(self, message: str, ast_type: Optional[str] = None):
        """Initialize normalization exception.
        
        Args:
            message: Error message.
            ast_type: Type of AST that failed to normalize.
        """
        self.ast_type = ast_type
        details = f"AST type: {ast_type}" if ast_type else None
        super().__init__(message, details)
