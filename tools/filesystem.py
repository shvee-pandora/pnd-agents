"""
Filesystem Tool

Provides file system operations for agents including reading, writing,
listing, and managing files and directories.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file or directory."""
    path: str
    name: str
    is_file: bool
    is_directory: bool
    size: int
    extension: Optional[str]
    modified_time: float


class FilesystemTool:
    """
    Filesystem operations tool for agents.
    
    Provides safe file system operations with path validation
    and error handling.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the filesystem tool.
        
        Args:
            base_path: Optional base path to restrict operations to.
                      If not provided, operations are unrestricted.
        """
        self.base_path = Path(base_path).resolve() if base_path else None
    
    def _validate_path(self, path: str) -> Path:
        """
        Validate and resolve a path.
        
        Args:
            path: The path to validate.
            
        Returns:
            Resolved Path object.
            
        Raises:
            ValueError: If path is outside base_path (when set).
        """
        resolved = Path(path).resolve()
        
        if self.base_path:
            try:
                resolved.relative_to(self.base_path)
            except ValueError:
                raise ValueError(
                    f"Path '{path}' is outside allowed base path '{self.base_path}'"
                )
        
        return resolved
    
    def read_file(self, path: str, encoding: str = 'utf-8') -> str:
        """
        Read the contents of a file.
        
        Args:
            path: Path to the file.
            encoding: File encoding (default: utf-8).
            
        Returns:
            File contents as string.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If path is invalid.
        """
        file_path = self._validate_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        return file_path.read_text(encoding=encoding)
    
    def write_file(
        self,
        path: str,
        content: str,
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> str:
        """
        Write content to a file.
        
        Args:
            path: Path to the file.
            content: Content to write.
            encoding: File encoding (default: utf-8).
            create_dirs: Create parent directories if needed.
            
        Returns:
            Absolute path to the written file.
        """
        file_path = self._validate_path(path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_text(content, encoding=encoding)
        return str(file_path)
    
    def read_json(self, path: str) -> Dict[str, Any]:
        """
        Read and parse a JSON file.
        
        Args:
            path: Path to the JSON file.
            
        Returns:
            Parsed JSON as dictionary.
        """
        content = self.read_file(path)
        return json.loads(content)
    
    def write_json(
        self,
        path: str,
        data: Union[Dict, List],
        indent: int = 2
    ) -> str:
        """
        Write data to a JSON file.
        
        Args:
            path: Path to the JSON file.
            data: Data to serialize.
            indent: JSON indentation (default: 2).
            
        Returns:
            Absolute path to the written file.
        """
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        return self.write_file(path, content)
    
    def list_directory(
        self,
        path: str,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> List[FileInfo]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory.
            pattern: Optional glob pattern to filter files.
            recursive: Whether to list recursively.
            
        Returns:
            List of FileInfo objects.
        """
        dir_path = self._validate_path(path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        if pattern:
            if recursive:
                items = dir_path.rglob(pattern)
            else:
                items = dir_path.glob(pattern)
        else:
            if recursive:
                items = dir_path.rglob('*')
            else:
                items = dir_path.iterdir()
        
        result = []
        for item in items:
            stat = item.stat()
            result.append(FileInfo(
                path=str(item),
                name=item.name,
                is_file=item.is_file(),
                is_directory=item.is_dir(),
                size=stat.st_size,
                extension=item.suffix if item.is_file() else None,
                modified_time=stat.st_mtime
            ))
        
        return result
    
    def exists(self, path: str) -> bool:
        """
        Check if a path exists.
        
        Args:
            path: Path to check.
            
        Returns:
            True if path exists.
        """
        try:
            file_path = self._validate_path(path)
            return file_path.exists()
        except ValueError:
            return False
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        try:
            file_path = self._validate_path(path)
            return file_path.is_file()
        except ValueError:
            return False
    
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory."""
        try:
            file_path = self._validate_path(path)
            return file_path.is_dir()
        except ValueError:
            return False
    
    def create_directory(self, path: str, parents: bool = True) -> str:
        """
        Create a directory.
        
        Args:
            path: Path to create.
            parents: Create parent directories if needed.
            
        Returns:
            Absolute path to the created directory.
        """
        dir_path = self._validate_path(path)
        dir_path.mkdir(parents=parents, exist_ok=True)
        return str(dir_path)
    
    def delete(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete.
            recursive: For directories, delete recursively.
            
        Returns:
            True if deletion was successful.
        """
        target_path = self._validate_path(path)
        
        if not target_path.exists():
            return False
        
        if target_path.is_file():
            target_path.unlink()
        elif target_path.is_dir():
            if recursive:
                shutil.rmtree(target_path)
            else:
                target_path.rmdir()
        
        return True
    
    def copy(self, source: str, destination: str) -> str:
        """
        Copy a file or directory.
        
        Args:
            source: Source path.
            destination: Destination path.
            
        Returns:
            Absolute path to the destination.
        """
        src_path = self._validate_path(source)
        dst_path = self._validate_path(destination)
        
        if src_path.is_file():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        elif src_path.is_dir():
            shutil.copytree(src_path, dst_path)
        else:
            raise ValueError(f"Source does not exist: {source}")
        
        return str(dst_path)
    
    def move(self, source: str, destination: str) -> str:
        """
        Move a file or directory.
        
        Args:
            source: Source path.
            destination: Destination path.
            
        Returns:
            Absolute path to the destination.
        """
        src_path = self._validate_path(source)
        dst_path = self._validate_path(destination)
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        
        return str(dst_path)
    
    def get_file_info(self, path: str) -> FileInfo:
        """
        Get information about a file or directory.
        
        Args:
            path: Path to get info for.
            
        Returns:
            FileInfo object with file details.
        """
        file_path = self._validate_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        stat = file_path.stat()
        return FileInfo(
            path=str(file_path),
            name=file_path.name,
            is_file=file_path.is_file(),
            is_directory=file_path.is_dir(),
            size=stat.st_size,
            extension=file_path.suffix if file_path.is_file() else None,
            modified_time=stat.st_mtime
        )


# Convenience function for quick file operations
def read_file(path: str) -> str:
    """Quick read file function."""
    return FilesystemTool().read_file(path)


def write_file(path: str, content: str) -> str:
    """Quick write file function."""
    return FilesystemTool().write_file(path, content)


def read_json(path: str) -> Dict[str, Any]:
    """Quick read JSON function."""
    return FilesystemTool().read_json(path)


def write_json(path: str, data: Union[Dict, List]) -> str:
    """Quick write JSON function."""
    return FilesystemTool().write_json(path, data)
