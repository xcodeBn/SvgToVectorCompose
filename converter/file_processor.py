"""File and directory processing module for SVG conversion."""

import os
import logging
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConversionReport:
    """Report of conversion process results."""
    total_files: int
    successful_conversions: int
    failed_conversions: int
    errors: List[str]
    output_files: List[Path]

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_conversions / self.total_files) * 100


class FileProcessor:
    """Handles file and directory operations for SVG conversion."""
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Validate input directory
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {self.input_dir}")
        if not self.input_dir.is_dir():
            raise NotADirectoryError(f"Input path is not a directory: {self.input_dir}")

    def scan_directory(self, input_dir: Optional[Path] = None) -> List[Path]:
        """Recursively scan directory for SVG files."""
        scan_dir = input_dir or self.input_dir
        svg_files = []
        
        try:
            for root, dirs, files in os.walk(scan_dir):
                root_path = Path(root)
                
                for file in files:
                    file_path = root_path / file
                    if self.validate_svg_file(file_path):
                        svg_files.append(file_path)
                        
            logger.info(f"Found {len(svg_files)} SVG files in {scan_dir}")
            return sorted(svg_files)
            
        except PermissionError as e:
            logger.error(f"Permission denied accessing directory {scan_dir}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error scanning directory {scan_dir}: {e}")
            raise

    def validate_svg_file(self, svg_path: Path) -> bool:
        """Validate if file is a valid SVG file."""
        try:
            # Check file extension
            if not svg_path.suffix.lower() == '.svg':
                return False
                
            # Check if file exists and is readable
            if not svg_path.exists() or not svg_path.is_file():
                return False
                
            # Check if file is not empty
            if svg_path.stat().st_size == 0:
                logger.warning(f"SVG file is empty: {svg_path}")
                return False
                
            # Basic SVG content validation
            try:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    content = f.read(1024)  # Read first 1KB
                    if '<svg' not in content.lower():
                        logger.warning(f"File doesn't appear to contain SVG content: {svg_path}")
                        return False
            except UnicodeDecodeError:
                logger.warning(f"File is not valid UTF-8: {svg_path}")
                return False
            except Exception as e:
                logger.warning(f"Error reading file {svg_path}: {e}")
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"Error validating SVG file {svg_path}: {e}")
            return False

    def create_output_structure(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """Create output directory structure mirroring input structure."""
        if output_path is None:
            # Calculate relative path from input_dir to input_path
            try:
                relative_path = input_path.relative_to(self.input_dir)
                output_path = self.output_dir / relative_path.parent
            except ValueError:
                # input_path is not relative to input_dir
                output_path = self.output_dir
        
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created output directory: {output_path}")
            return output_path
            
        except PermissionError as e:
            logger.error(f"Permission denied creating directory {output_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating directory {output_path}: {e}")
            raise

    def write_kotlin_file(self, content: str, output_path: Path) -> bool:
        """Write Kotlin content to file."""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file with UTF-8 encoding
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.debug(f"Successfully wrote Kotlin file: {output_path}")
            return True
            
        except PermissionError as e:
            logger.error(f"Permission denied writing file {output_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error writing file {output_path}: {e}")
            return False

    def get_output_path(self, input_svg_path: Path) -> Path:
        """Generate output Kotlin file path from input SVG path."""
        try:
            # Calculate relative path from input directory
            relative_path = input_svg_path.relative_to(self.input_dir)
            
            # Convert filename to PascalCase (proper Kotlin convention)
            pascal_case_name = self._convert_to_pascal_case(relative_path.stem)
            kotlin_filename = pascal_case_name + '.kt'
            
            # Build full output path
            output_path = self.output_dir / relative_path.parent / kotlin_filename
            
            return output_path
            
        except ValueError:
            # Fallback if input_svg_path is not relative to input_dir
            pascal_case_name = self._convert_to_pascal_case(input_svg_path.stem)
            kotlin_filename = pascal_case_name + '.kt'
            return self.output_dir / kotlin_filename

    def _convert_to_pascal_case(self, filename: str) -> str:
        """Convert filename to PascalCase for Kotlin file naming."""
        # Import here to avoid circular imports
        import re
        
        # Replace special characters with underscores, then split
        normalized = re.sub(r'[^a-zA-Z0-9]+', '_', filename)
        
        # Split by underscores and convert to PascalCase
        words = [word for word in normalized.split('_') if word]
        
        # Handle edge cases
        if not words:
            return "Icon"
        
        # Convert each word to title case
        pascal_words = []
        for word in words:
            if word.isdigit():
                # If word is all digits, prefix with something
                if not pascal_words:  # First word is digits
                    pascal_words.append("Icon" + word)
                else:
                    pascal_words.append(word)
            else:
                pascal_words.append(word.capitalize())
        
        result = ''.join(pascal_words)
        
        # If filename starts with digit, prefix with Icon
        if result and result[0].isdigit():
            result = "Icon" + result
        
        # Handle Kotlin keywords
        kotlin_keywords = {
            'class', 'interface', 'object', 'fun', 'val', 'var', 'when', 'for',
            'while', 'do', 'if', 'else', 'try', 'catch', 'finally', 'throw',
            'return', 'break', 'continue', 'true', 'false', 'null', 'this',
            'super', 'is', 'in', 'as', 'package', 'import', 'typealias'
        }
        
        if result.lower() in kotlin_keywords:
            result = result + "Icon"
        
        return result

    def clean_output_directory(self, confirm: bool = False) -> bool:
        """Clean output directory of existing files."""
        if not confirm:
            logger.warning("clean_output_directory called without confirmation")
            return False
            
        try:
            if self.output_dir.exists():
                for item in self.output_dir.rglob('*'):
                    if item.is_file():
                        item.unlink()
                        logger.debug(f"Removed file: {item}")
                        
                # Remove empty directories
                for item in sorted(self.output_dir.rglob('*'), reverse=True):
                    if item.is_dir() and not any(item.iterdir()):
                        item.rmdir()
                        logger.debug(f"Removed empty directory: {item}")
                        
                logger.info(f"Cleaned output directory: {self.output_dir}")
                return True
            else:
                logger.info(f"Output directory doesn't exist: {self.output_dir}")
                return True
                
        except Exception as e:
            logger.error(f"Error cleaning output directory {self.output_dir}: {e}")
            return False

    def generate_progress_report(self, processed_files: int, total_files: int) -> str:
        """Generate progress report string."""
        if total_files == 0:
            return "No files to process"
            
        percentage = (processed_files / total_files) * 100
        return f"Progress: {processed_files}/{total_files} ({percentage:.1f}%)"

    def get_file_stats(self, file_path: Path) -> Dict[str, any]:
        """Get file statistics."""
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK)
            }
        except Exception as e:
            logger.warning(f"Error getting stats for {file_path}: {e}")
            return {
                'size': 0,
                'modified': 0,
                'readable': False,
                'writable': False
            }

    def backup_existing_file(self, file_path: Path) -> Optional[Path]:
        """Create backup of existing file if it exists."""
        if not file_path.exists():
            return None
            
        try:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            counter = 1
            
            # Find unique backup filename
            while backup_path.exists():
                backup_path = file_path.with_suffix(f'.backup{counter}{file_path.suffix}')
                counter += 1
                
            # Copy file to backup
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.warning(f"Failed to create backup for {file_path}: {e}")
            return None

    def list_output_files(self) -> List[Path]:
        """List all generated Kotlin files in output directory."""
        if not self.output_dir.exists():
            return []
            
        kotlin_files = []
        for file_path in self.output_dir.rglob('*.kt'):
            if file_path.is_file():
                kotlin_files.append(file_path)
                
        return sorted(kotlin_files)