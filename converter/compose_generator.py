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
        
        # Generate path definitions and helper methods
        path_definitions, helper_methods = self._generate_all_paths_with_splitting(svg_data, icon_name)
        
        # Build package name with subdirectory structure
        package_name = self._build_package_name(relative_path)
        
        # Build the complete Kotlin file content
        kotlin_code = f"""package {package_name}

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathFillType
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.group
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

val {icon_name}: ImageVector
    get() {{
        if (_{icon_name} != null) return _{icon_name}!!
        
        _{icon_name} = ImageVector.Builder(
            name = "{icon_name}",
            defaultWidth = {svg_data.width:.1f}.dp,
            defaultHeight = {svg_data.height:.1f}.dp,
            viewportWidth = {svg_data.viewbox.width:.1f}f,
            viewportHeight = {svg_data.viewbox.height:.1f}f
        ).apply {{
{path_definitions}
        }}.build()
        
        return _{icon_name}!!
    }}

private var _{icon_name}: ImageVector? = null

{helper_methods}"""

        return self.format_kotlin_code(kotlin_code)

    def _generate_all_paths_with_splitting(self, svg_data: SVGData, icon_name: str) -> tuple[str, str]:
        """Generate all path definitions with automatic splitting for large paths."""
        MAX_COMMANDS_PER_METHOD = 300  # Threshold to avoid JVM method size limits
        
        path_codes = []
        helper_methods = []
        helper_counter = 0
        
        # Generate standalone paths
        for path_data in svg_data.paths:
            commands = self._parse_path_commands(path_data.d)
            
            if len(commands) > MAX_COMMANDS_PER_METHOD:
                # Split large path into multiple helper methods
                helper_calls = self._generate_split_path_methods(
                    path_data, commands, icon_name, helper_counter, MAX_COMMANDS_PER_METHOD
                )
                path_codes.extend(helper_calls['calls'])
                helper_methods.extend(helper_calls['methods'])
                helper_counter += len(helper_calls['methods'])
            else:
                # Generate normal path
                path_code = self.generate_path_code(path_data)
                if path_code:
                    path_codes.append(path_code)
        
        # Generate grouped paths (handle large groups similarly)
        for group_data in svg_data.groups:
            group_code = self.generate_group_code(group_data)
            if group_code:
                path_codes.append(group_code)
        
        # Join results
        path_definitions = '\n'.join(path_codes)
        helper_methods_str = '\n\n'.join(helper_methods) if helper_methods else ""
        
        return path_definitions, helper_methods_str

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

    def _generate_split_path_methods(self, path_data: PathData, commands: list, icon_name: str, 
                                   helper_counter: int, max_commands: int) -> dict:
        """Split a large path into multiple helper methods."""
        # Split commands into chunks
        command_chunks = [commands[i:i + max_commands] for i in range(0, len(commands), max_commands)]
        
        helper_methods = []
        method_calls = []
        
        # Generate helper methods for each chunk
        for i, chunk in enumerate(command_chunks):
            method_name = f"build{icon_name}Path{helper_counter + i + 1}"
            
            # Create a temporary path data for this chunk
            chunk_path_data = self._create_chunk_path_data(path_data, chunk)
            
            # Generate the helper method
            helper_method = self._generate_path_helper_method(chunk_path_data, method_name)
            helper_methods.append(helper_method)
            
            # Generate the method call
            method_call = f"            {method_name}()"
            method_calls.append(method_call)
        
        return {
            'methods': helper_methods,
            'calls': method_calls
        }

    def _create_chunk_path_data(self, original_path_data: PathData, commands: list) -> PathData:
        """Create a PathData object for a chunk of commands."""
        # Reconstruct path data string from commands
        path_string = self._commands_to_path_string(commands)
        
        # Create a new PathData with the same properties but chunked path
        import copy
        chunk_path_data = copy.deepcopy(original_path_data)
        chunk_path_data.d = path_string
        
        return chunk_path_data

    def _commands_to_path_string(self, commands: list) -> str:
        """Convert command list back to SVG path string."""
        path_parts = []
        
        for command in commands:
            if command['type'] == 'M':
                path_parts.append(f"M {command['x']:.2f},{command['y']:.2f}")
            elif command['type'] == 'L':
                path_parts.append(f"L {command['x']:.2f},{command['y']:.2f}")
            elif command['type'] == 'H':
                path_parts.append(f"H {command['x']:.2f}")
            elif command['type'] == 'V':
                path_parts.append(f"V {command['y']:.2f}")
            elif command['type'] == 'C':
                path_parts.append(f"C {command['x1']:.2f},{command['y1']:.2f} {command['x2']:.2f},{command['y2']:.2f} {command['x']:.2f},{command['y']:.2f}")
            elif command['type'] == 'Z':
                path_parts.append("Z")
                
        return ' '.join(path_parts)

    def _generate_path_helper_method(self, path_data: PathData, method_name: str) -> str:
        """Generate a helper method for a path chunk."""
        # Get colors and path parameters (similar to generate_path_code)
        fill_opacity = getattr(path_data, 'fill_opacity', 1.0)
        stroke_opacity = getattr(path_data, 'stroke_opacity', 1.0)
        
        fill_color = self._convert_color_to_compose_with_opacity(path_data.fill, fill_opacity)
        stroke_color = self._convert_color_to_compose_with_opacity(path_data.stroke, stroke_opacity) if path_data.stroke != "none" else None
        
        # Build path parameters
        path_params = []
        if path_data.fill != "none" and fill_color:
            path_params.append(f"fill = SolidColor({fill_color})")
            
        if path_data.fill_rule.lower() == "evenodd":
            path_params.append(f"pathFillType = PathFillType.EvenOdd")
        
        if stroke_color and path_data.stroke != "none":
            path_params.append(f"stroke = SolidColor({stroke_color})")
            if path_data.stroke_width > 0:
                path_params.append(f"strokeLineWidth = {path_data.stroke_width:.1f}f")
        
        # Format path parameters
        if path_params:
            param_lines = ["    path("]
            for i, param in enumerate(path_params):
                comma = "," if i < len(path_params) - 1 else ""
                param_lines.append(f"        {param}{comma}")
            param_lines.append("    ) {")
        else:
            param_lines = ["    path() {"]
        
        # Generate path commands
        path_commands = self._format_path_data(path_data.d, 2)
        
        # Build complete method
        method_lines = [f"private fun ImageVector.Builder.{method_name}() {{"]
        method_lines.extend(param_lines)
        method_lines.extend(path_commands)
        method_lines.append("    }")
        method_lines.append("}")
        
        return '\n'.join(method_lines)

    def generate_path_code(self, path_data: PathData, indent_level: int = 3) -> str:
        """Generate Compose path code from PathData."""
        if not path_data.d:
            return ""
            
        indent = "    " * indent_level
        
        # Determine fill type
        fill_type = "PathFillType.NonZero"
        if path_data.fill_rule.lower() == "evenodd":
            fill_type = "PathFillType.EvenOdd"
        
        # Convert colors with opacity
        fill_opacity = getattr(path_data, 'fill_opacity', 1.0)
        stroke_opacity = getattr(path_data, 'stroke_opacity', 1.0)
        
        fill_color = self._convert_color_to_compose_with_opacity(path_data.fill, fill_opacity)
        stroke_color = self._convert_color_to_compose_with_opacity(path_data.stroke, stroke_opacity) if path_data.stroke != "none" else None
        
        # Build path block with proper parameters
        path_params = []
        
        # Add fill color if not none - use SolidColor wrapper
        if path_data.fill != "none" and fill_color:
            path_params.append(f"fill = SolidColor({fill_color})")
            
        # Add fill type if not default
        if path_data.fill_rule.lower() == "evenodd":
            path_params.append(f"pathFillType = {fill_type}")
        
        # Add stroke if present
        if stroke_color and path_data.stroke != "none":
            path_params.append(f"stroke = SolidColor({stroke_color})")
            if path_data.stroke_width > 0:
                path_params.append(f"strokeLineWidth = {path_data.stroke_width:.1f}f")
        
        # Build the path opening with proper formatting
        if path_params:
            path_lines = [f"{indent}path("]
            for i, param in enumerate(path_params):
                # Add comma to all parameters except the last one
                comma = "," if i < len(path_params) - 1 else ""
                path_lines.append(f"{indent}    {param}{comma}")
            path_lines.append(f"{indent}) {{")
        else:
            path_lines = [f"{indent}path() {{"]
        
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
        group_lines = [f"{indent}group() {{"]
        
        # Add all child paths, applying group opacity to individual path colors
        for child in group_data.children:
            if isinstance(child, PathData):
                # Apply group opacity to this path's colors
                child_with_opacity = self._apply_group_opacity_to_path(child, group_data.opacity)
                child_code = self.generate_path_code(child_with_opacity, indent_level + 1)
                if child_code:
                    group_lines.append(child_code)
        
        group_lines.append(f"{indent}}}")
        
        return '\n'.join(group_lines)

    def _apply_group_opacity_to_path(self, path_data, group_opacity: float):
        """Apply group opacity to individual path colors."""
        if group_opacity >= 1.0:
            return path_data  # No opacity change needed
        
        # Create a copy of the path data to modify
        import copy
        modified_path = copy.deepcopy(path_data)
        
        # Apply opacity to fill color if it exists
        if hasattr(modified_path, 'fill') and modified_path.fill != "none":
            modified_path.fill_opacity = getattr(modified_path, 'fill_opacity', 1.0) * group_opacity
        
        # Apply opacity to stroke color if it exists  
        if hasattr(modified_path, 'stroke') and modified_path.stroke != "none":
            modified_path.stroke_opacity = getattr(modified_path, 'stroke_opacity', 1.0) * group_opacity
            
        return modified_path

    def _format_path_data(self, path_data: str, indent_level: int) -> List[str]:
        """Format SVG path data into Compose path commands."""
        indent = "    " * indent_level
        lines = []
        
        # Split path data into commands
        commands = self._parse_path_commands(path_data)
        
        for command in commands:
            if command['type'] == 'M':
                lines.append(f"{indent}moveTo({command['x']:.0f}f, {command['y']:.0f}f)")
            elif command['type'] == 'L':
                lines.append(f"{indent}lineTo({command['x']:.0f}f, {command['y']:.0f}f)")
            elif command['type'] == 'H':
                if command.get('relative', False):
                    lines.append(f"{indent}horizontalLineToRelative({command['x']:.0f}f)")
                else:
                    lines.append(f"{indent}horizontalLineTo({command['x']:.0f}f)")
            elif command['type'] == 'V':
                if command.get('relative', False):
                    lines.append(f"{indent}verticalLineToRelative({command['y']:.0f}f)")
                else:
                    lines.append(f"{indent}verticalLineTo({command['y']:.0f}f)")
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
                            commands.append({'type': 'H', 'x': x, 'relative': is_relative})
                            current_x += x
                        else:
                            commands.append({'type': 'H', 'x': x, 'relative': is_relative})
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
                            commands.append({'type': 'V', 'y': y, 'relative': is_relative})
                            current_y += y
                        else:
                            commands.append({'type': 'V', 'y': y, 'relative': is_relative})
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

    def _convert_color_to_compose_with_opacity(self, color: str, opacity: float = 1.0) -> Optional[str]:
        """Convert SVG color to Compose Color with opacity."""
        if not color or color.lower() == "none":
            return None
            
        # Get the base color
        base_color = self._convert_color_to_compose(color)
        if not base_color:
            return None
            
        # If opacity is 1.0, return base color as-is
        if opacity >= 1.0:
            return base_color
            
        # Apply opacity to the color
        if base_color.startswith("Color(0xFF"):
            # Extract hex value and apply alpha
            hex_part = base_color[10:-1]  # Remove "Color(0xFF" and ")"
            alpha_hex = format(int(opacity * 255), '02X')
            return f"Color(0x{alpha_hex}{hex_part})"
        else:
            # For named colors, use copy(alpha = x)
            return f"{base_color}.copy(alpha = {opacity:.2f}f)"

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