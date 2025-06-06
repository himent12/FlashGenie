"""
File handling utilities for FlashGenie.

This module provides utility functions for file operations,
path handling, and file format detection.
"""

import os
import shutil
from typing import List, Optional, Dict, Any
from pathlib import Path


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: Path) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    return file_path.stat().st_size if file_path.exists() else 0


def get_file_extension(file_path: Path) -> str:
    """
    Get the file extension in lowercase.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (including the dot)
    """
    return file_path.suffix.lower()


def is_supported_import_format(file_path: Path) -> bool:
    """
    Check if a file format is supported for import.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the format is supported
    """
    from flashgenie.config import SUPPORTED_IMPORT_FORMATS
    return get_file_extension(file_path) in SUPPORTED_IMPORT_FORMATS


def is_supported_export_format(file_path: Path) -> bool:
    """
    Check if a file format is supported for export.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the format is supported
    """
    from flashgenie.config import SUPPORTED_EXPORT_FORMATS
    return get_file_extension(file_path) in SUPPORTED_EXPORT_FORMATS


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "untitled"
    
    return safe_name


def backup_file(file_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory for backup (uses same directory if None)
        
    Returns:
        Path to the backup file
    """
    if backup_dir is None:
        backup_dir = file_path.parent
    
    ensure_directory(backup_dir)
    
    # Generate backup filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    # Copy file
    shutil.copy2(file_path, backup_path)
    
    return backup_path


def cleanup_temp_files(temp_dir: Path, max_age_hours: int = 24) -> int:
    """
    Clean up temporary files older than specified age.
    
    Args:
        temp_dir: Directory containing temporary files
        max_age_hours: Maximum age in hours
        
    Returns:
        Number of files removed
    """
    if not temp_dir.exists():
        return 0
    
    import time
    cutoff_time = time.time() - (max_age_hours * 3600)
    removed_count = 0
    
    for file_path in temp_dir.iterdir():
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                removed_count += 1
            except OSError:
                # Skip files that can't be removed
                continue
    
    return removed_count


def get_available_filename(file_path: Path) -> Path:
    """
    Get an available filename by adding a number suffix if needed.
    
    Args:
        file_path: Desired file path
        
    Returns:
        Available file path
    """
    if not file_path.exists():
        return file_path
    
    base_path = file_path.parent
    stem = file_path.stem
    suffix = file_path.suffix
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = base_path / new_name
        
        if not new_path.exists():
            return new_path
        
        counter += 1


def read_text_file(file_path: Path, encoding: str = 'utf-8') -> str:
    """
    Read a text file with error handling.
    
    Args:
        file_path: Path to the file
        encoding: File encoding
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If encoding is wrong
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for enc in encodings:
            if enc == encoding:
                continue
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, re-raise the original error
        raise


def write_text_file(file_path: Path, content: str, encoding: str = 'utf-8') -> None:
    """
    Write content to a text file with error handling.
    
    Args:
        file_path: Path to the file
        content: Content to write
        encoding: File encoding
    """
    ensure_directory(file_path.parent)
    
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)


def get_directory_size(directory: Path) -> int:
    """
    Calculate the total size of a directory.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    if not directory.exists():
        return 0
    
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                total_size += file_path.stat().st_size
            except OSError:
                # Skip files that can't be accessed
                continue
    
    return total_size


def find_files_by_pattern(directory: Path, pattern: str) -> List[Path]:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match
        
    Returns:
        List of matching file paths
    """
    if not directory.exists():
        return []
    
    return list(directory.glob(pattern))


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get comprehensive information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    if not file_path.exists():
        return {"exists": False}
    
    stat = file_path.stat()
    
    return {
        "exists": True,
        "name": file_path.name,
        "stem": file_path.stem,
        "suffix": file_path.suffix,
        "size": stat.st_size,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "is_file": file_path.is_file(),
        "is_directory": file_path.is_dir(),
        "absolute_path": str(file_path.absolute()),
        "parent": str(file_path.parent)
    }
