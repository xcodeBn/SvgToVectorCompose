"""Compose Vector Drawable code generation module."""

import re
import logging
from typing import List, Optional
from .svg_parser import SVGData, PathData, GroupData

logger = logging.getLogger(__name__)


class ComposeGenerator:
    """Generates Compose ImageVector code from SVG data."""
    
    def __init__(self, package_name: str = "com.example.icons"):
        self.package_name = package_name
        
    def generate_vector_drawable(self, svg_data: SVGData, class_name: str, relative_path: str = None) -> str:
        """Generate complete Compose ImageVector Kotlin code."""
        # Convert filename to PascalCase for class name
        icon_name = self.convert_to_pascal_case(class_name)
        private_var_name = f"_{self._to_camel_case(icon_name)}"
        
        # Generate path definitions
        path_definitions = self._generate_all_paths(svg_data)
        
        # Build package name with subdirectory structure
        package_name = self._build_package_name(relative_path)
        
        # Build the complete Kotlin file content
        kotlin_code = f"""package {package_name}

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathFillType
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

val {icon_name}: ImageVector
    get() {{
        if ({private_var_name} != null) {{
            return {private_var_name}!!
        }}
        {private_var_name} = ImageVector.Builder(
            name = "{icon_name}",
            defaultWidth = {svg_data.width:.1f}.dp,
            defaultHeight = {svg_data.height:.1f}.dp,
            viewportWidth = {svg_data.viewbox.width:.1f}f,
            viewportHeight = {svg_data.viewbox.height:.1f}f
        ).apply {{
{path_definitions}
        }}.build()
        return {private_var_name}!!
    }}

private var {private_var_name}: ImageVector? = null"""

        return self.format_kotlin_code(kotlin_code)

    def _generate_all_paths(self, svg_data: SVGData) -> str:
        """Generate all path definitions from SVG data."""
        path_codes = []
        
        # Generate standalone paths
        for path_data in svg_data.paths:
            path_code = self.generate_path_code(path_data)
            if path_code:
                path_codes.append(path_code)
        
        # Generate grouped paths
        for group_data in svg_data.groups:
            group_code = self.generate_group_code(group_data)
            if group_code:
                path_codes.append(group_code)
        
        # Join all path codes with proper indentation
        return '\n'.join(path_codes)

    def generate_path_code(self, path_data: PathData, indent_level: int = 3) -> str:
        """Generate Compose path code from PathData."""
        if not path_data.d:
            return ""
            
        indent = "    " * indent_level
        
        # Determine fill type
        fill_type = "PathFillType.NonZero"
        if path_data.fill_rule.lower() == "evenodd":
            fill_type = "PathFillType.EvenOdd"
        
        # Convert colors
        fill_color = self._convert_color_to_compose(path_data.fill)
        stroke_color = self._convert_color_to_compose(path_data.stroke) if path_data.stroke != "none" else None
        
        # Build path block
        path_lines = [f"{indent}path("]
        
        # Add fill color if not none
        if path_data.fill != "none" and fill_color:
            path_lines.append(f"{indent}    fill = {fill_color},")
            
        # Add fill type if not default
        if path_data.fill_rule.lower() == "evenodd":
            path_lines.append(f"{indent}    fillType = {fill_type},")
        
        # Add stroke if present
        if stroke_color and path_data.stroke != "none":
            path_lines.append(f"{indent}    stroke = {stroke_color},")
            if path_data.stroke_width > 0:
                path_lines.append(f"{indent}    strokeLineWidth = {path_data.stroke_width:.1f}f,")
        
        path_lines.append(f"{indent}) {{")
        
        # Add path data with proper formatting
        formatted_path_data = self._format_path_data(path_data.d, indent_level + 1)
        path_lines.extend(formatted_path_data)
        
        path_lines.append(f"{indent}}}")
        
        return '\n'.join(path_lines)

    def generate_group_code(self, group_data: GroupData, indent_level: int = 3) -> str:
        """Generate Compose group code from GroupData."""
        if not group_data.children:
            return ""
            
        indent = "    " * indent_level
        group_lines = [f"{indent}group("]
        
        # Add group properties if they exist
        if group_data.opacity < 1.0:
            group_lines.append(f"{indent}    alpha = {group_data.opacity:.2f}f,")
            
        group_lines.append(f"{indent}) {{")
        
        # Add all child paths
        for child in group_data.children:
            if isinstance(child, PathData):
                child_code = self.generate_path_code(child, indent_level + 1)
                if child_code:
                    group_lines.append(child_code)
        
        group_lines.append(f"{indent}}}")
        
        return '\n'.join(group_lines)

    def _format_path_data(self, path_data: str, indent_level: int) -> List[str]:
        """Format SVG path data into Compose path commands."""
        indent = "    " * indent_level
        lines = []
        
        # Split path data into commands
        commands = self._parse_path_commands(path_data)
        
        for command in commands:
            if command['type'] == 'M':
                lines.append(f"{indent}moveTo({command['x']:.2f}f, {command['y']:.2f}f)")
            elif command['type'] == 'L':
                lines.append(f"{indent}lineTo({command['x']:.2f}f, {command['y']:.2f}f)")
            elif command['type'] == 'H':
                lines.append(f"{indent}horizontalLineTo({command['x']:.2f}f)")
            elif command['type'] == 'V':
                lines.append(f"{indent}verticalLineTo({command['y']:.2f}f)")
            elif command['type'] == 'C':
                lines.append(f"{indent}curveTo({command['x1']:.2f}f, {command['y1']:.2f}f, {command['x2']:.2f}f, {command['y2']:.2f}f, {command['x']:.2f}f, {command['y']:.2f}f)")
            elif command['type'] == 'S':
                lines.append(f"{indent}reflectiveCurveTo({command['x2']:.2f}f, {command['y2']:.2f}f, {command['x']:.2f}f, {command['y']:.2f}f)")
            elif command['type'] == 'Q':
                lines.append(f"{indent}quadTo({command['x1']:.2f}f, {command['y1']:.2f}f, {command['x']:.2f}f, {command['y']:.2f}f)")
            elif command['type'] == 'T':
                lines.append(f"{indent}reflectiveQuadTo({command['x']:.2f}f, {command['y']:.2f}f)")
            elif command['type'] == 'A':
                lines.append(f"{indent}arcTo({command['rx']:.2f}f, {command['ry']:.2f}f, {command['rotation']:.2f}f, {command['large_arc']}, {command['sweep']}, {command['x']:.2f}f, {command['y']:.2f}f)")
            elif command['type'] == 'Z':
                lines.append(f"{indent}close()")
        
        return lines

    def _parse_path_commands(self, path_data: str) -> List[dict]:
        """Parse SVG path data string into structured commands."""
        commands = []
        
        # Normalize the path data - handle comma-separated coordinates
        path_data = re.sub(r'\s+', ' ', path_data.strip())
        
        # Replace commas with spaces, but be careful with negative numbers
        path_data = re.sub(r',', ' ', path_data)
        
        # Handle concatenated numbers like "125,30" -> "125 30"
        path_data = re.sub(r'([+-]?\d*\.?\d+)([+-]\d*\.?\d+)', r'\1 \2', path_data)
        
        # Ensure proper spacing around path commands
        path_data = re.sub(r'([MmLlHhVvCcSsQqTtAaZz])', r' \1 ', path_data)
        path_data = re.sub(r'\s+', ' ', path_data.strip())
        
        # Split into tokens
        tokens = path_data.split()
        i = 0
        current_x, current_y = 0.0, 0.0
        
        while i < len(tokens):
            cmd = tokens[i].upper()
            is_relative = tokens[i].islower()
            i += 1
            
            if cmd == 'M':
                if i + 1 < len(tokens):
                    try:
                        x, y = float(tokens[i]), float(tokens[i + 1])
                        if is_relative:
                            x += current_x
                            y += current_y
                        commands.append({'type': 'M', 'x': x, 'y': y})
                        current_x, current_y = x, y
                        i += 2
                    except ValueError:
                        logger.warning(f"Invalid coordinates for M command: {tokens[i:i+2]}")
                        i += 2
            elif cmd == 'L':
                if i + 1 < len(tokens):
                    try:
                        x, y = float(tokens[i]), float(tokens[i + 1])
                        if is_relative:
                            x += current_x
                            y += current_y
                        commands.append({'type': 'L', 'x': x, 'y': y})
                        current_x, current_y = x, y
                        i += 2
                    except ValueError:
                        logger.warning(f"Invalid coordinates for L command: {tokens[i:i+2]}")
                        i += 2
            elif cmd == 'H':
                if i < len(tokens):
                    try:
                        x = float(tokens[i])
                        if is_relative:
                            x += current_x
                        commands.append({'type': 'H', 'x': x})
                        current_x = x
                        i += 1
                    except ValueError:
                        logger.warning(f"Invalid coordinate for H command: {tokens[i]}")
                        i += 1
            elif cmd == 'V':
                if i < len(tokens):
                    try:
                        y = float(tokens[i])
                        if is_relative:
                            y += current_y
                        commands.append({'type': 'V', 'y': y})
                        current_y = y
                        i += 1
                    except ValueError:
                        logger.warning(f"Invalid coordinate for V command: {tokens[i]}")
                        i += 1
            elif cmd == 'C':
                if i + 5 < len(tokens):
                    try:
                        x1, y1 = float(tokens[i]), float(tokens[i + 1])
                        x2, y2 = float(tokens[i + 2]), float(tokens[i + 3])
                        x, y = float(tokens[i + 4]), float(tokens[i + 5])
                        if is_relative:
                            x1 += current_x
                            y1 += current_y
                            x2 += current_x
                            y2 += current_y
                            x += current_x
                            y += current_y
                        commands.append({'type': 'C', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'x': x, 'y': y})
                        current_x, current_y = x, y
                        i += 6
                    except ValueError:
                        logger.warning(f"Invalid coordinates for C command: {tokens[i:i+6]}")
                        i += 6
            elif cmd == 'Z':
                commands.append({'type': 'Z'})
            else:
                # Skip unknown commands
                i += 1
        
        return commands

    def _convert_color_to_compose(self, color: str) -> Optional[str]:
        """Convert SVG color to Compose Color."""
        if not color or color.lower() == "none":
            return None
            
        # Handle hex colors
        if color.startswith("#"):
            if len(color) == 7:  # #RRGGBB
                return f"Color(0xFF{color[1:].upper()})"
            elif len(color) == 4:  # #RGB
                r, g, b = color[1], color[2], color[3]
                return f"Color(0xFF{r}{r}{g}{g}{b}{b})"
        
        # Handle named colors
        if color.lower() == "black":
            return "Color.Black"
        elif color.lower() == "white":
            return "Color.White"
        elif color.lower() == "red":
            return "Color.Red"
        elif color.lower() == "green":
            return "Color.Green"
        elif color.lower() == "blue":
            return "Color.Blue"
        elif color.lower() == "transparent":
            return "Color.Transparent"
        
        # Default to black if can't parse
        logger.warning(f"Unknown color format: {color}, defaulting to black")
        return "Color.Black"

    def convert_to_pascal_case(self, snake_case: str) -> str:
        """Convert snake_case or kebab-case to PascalCase with Kotlin-safe naming."""
        # Handle both snake_case, kebab-case, and other separators
        words = re.split(r'[_\-\s\.@#\(\)\[\]]+', snake_case)
        
        # Clean and capitalize each word
        clean_words = []
        for word in words:
            if word:
                # Remove any remaining invalid characters and ensure alphanumeric
                clean_word = re.sub(r'[^a-zA-Z0-9]', '', word)
                if clean_word:
                    # Ensure doesn't start with number
                    if clean_word[0].isdigit():
                        clean_word = 'Icon' + clean_word
                    clean_words.append(clean_word.capitalize())
        
        # Join words and ensure result is valid
        result = ''.join(clean_words)
        
        # Fallback if empty or invalid
        if not result or not result[0].isalpha():
            result = 'Icon' + (result if result else 'Unknown')
        
        # Handle Kotlin keywords
        kotlin_keywords = {
            'class', 'object', 'interface', 'fun', 'val', 'var', 'if', 'else', 
            'when', 'for', 'while', 'do', 'try', 'catch', 'finally', 'return',
            'break', 'continue', 'throw', 'import', 'package', 'as', 'is', 'in'
        }
        
        if result.lower() in kotlin_keywords:
            result = result + 'Icon'
        
        return result

    def _to_camel_case(self, pascal_case: str) -> str:
        """Convert PascalCase to camelCase."""
        if not pascal_case:
            return pascal_case
        return pascal_case[0].lower() + pascal_case[1:]

    def _build_package_name(self, relative_path: str = None) -> str:
        """Build package name including subdirectory structure."""
        if not relative_path:
            return self.package_name
        
        # Convert file path to package path
        # Example: icons/actions/edit.kt -> icons.actions
        path_parts = []
        
        # Get directory parts (exclude filename)
        import os
        dir_path = os.path.dirname(relative_path)
        
        if dir_path:
            # Split directory path and normalize for package naming
            parts = dir_path.split(os.sep)
            for part in parts:
                if part:  # Skip empty parts
                    # Normalize package segment (replace dashes with underscores, etc.)
                    normalized_part = re.sub(r'[^a-zA-Z0-9]', '_', part.lower())
                    if normalized_part and not normalized_part[0].isdigit():
                        path_parts.append(normalized_part)
        
        if path_parts:
            return f"{self.package_name}.{'.'.join(path_parts)}"
        else:
            return self.package_name

    def format_kotlin_code(self, code: str) -> str:
        """Format Kotlin code with proper indentation."""
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            formatted_line = line.rstrip()
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)