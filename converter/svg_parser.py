"""SVG parsing module for extracting data from SVG files."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ViewBox:
    """Represents SVG viewBox dimensions."""
    x: float
    y: float
    width: float
    height: float

    @classmethod
    def from_string(cls, viewbox_str: str) -> 'ViewBox':
        """Parse viewBox string like '0 0 24 24' into ViewBox object."""
        try:
            values = [float(x) for x in viewbox_str.strip().split()]
            if len(values) == 4:
                return cls(values[0], values[1], values[2], values[3])
            else:
                raise ValueError(f"Invalid viewBox format: {viewbox_str}")
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse viewBox '{viewbox_str}': {e}")
            return cls(0, 0, 24, 24)  # Default fallback


@dataclass
class PathData:
    """Represents SVG path element data."""
    d: str
    fill: str = "black"
    stroke: str = "none"
    stroke_width: float = 0.0
    fill_rule: str = "nonzero"
    opacity: float = 1.0
    transform: Optional[str] = None

    def __post_init__(self):
        """Normalize and validate path data after initialization."""
        self.fill = self._normalize_color(self.fill)
        self.stroke = self._normalize_color(self.stroke)
        
    def _normalize_color(self, color: str) -> str:
        """Normalize color values to standard format."""
        if not color or color.lower() == "none":
            return "none"
        
        # Handle named colors
        named_colors = {
            "black": "#000000",
            "white": "#ffffff", 
            "red": "#ff0000",
            "green": "#008000",
            "blue": "#0000ff",
            "transparent": "none"
        }
        
        color_lower = color.lower()
        if color_lower in named_colors:
            return named_colors[color_lower]
            
        # Handle hex colors
        if color.startswith("#"):
            return color.upper()
            
        # Handle rgb/rgba colors - convert to hex
        rgb_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', color)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return f"#{r:02X}{g:02X}{b:02X}"
            
        return color


@dataclass 
class GroupData:
    """Represents SVG group element data."""
    transform: Optional[str] = None
    opacity: float = 1.0
    fill: str = "black"
    stroke: str = "none"
    children: List[Any] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class SVGData:
    """Complete SVG file data."""
    width: float
    height: float
    viewbox: ViewBox
    paths: List[PathData]
    groups: List[GroupData]
    filename: str

    def __post_init__(self):
        """Initialize empty lists if None."""
        if self.paths is None:
            self.paths = []
        if self.groups is None:
            self.groups = []


class SVGParser:
    """Parser for extracting data from SVG files."""
    
    def __init__(self):
        self.namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

    def parse_svg_file(self, svg_path: Path) -> SVGData:
        """Parse an SVG file and extract all relevant data."""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Store root for CSS class resolution
            self._current_root = root
            
            # Remove namespace prefixes for easier parsing
            self._remove_namespace_prefixes(root)
            
            # Extract basic SVG attributes
            width, height = self._extract_dimensions(root)
            viewbox = self.extract_viewbox(root)
            
            # Extract paths and groups
            paths = self.extract_paths(root)
            groups = self.extract_groups(root)
            
            return SVGData(
                width=width,
                height=height,
                viewbox=viewbox,
                paths=paths,
                groups=groups,
                filename=svg_path.stem
            )
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse SVG file {svg_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing {svg_path}: {e}")
            raise

    def _remove_namespace_prefixes(self, element):
        """Remove namespace prefixes from element tags recursively."""
        if '}' in element.tag:
            element.tag = element.tag.split('}')[1]
        for child in element:
            self._remove_namespace_prefixes(child)

    def _extract_dimensions(self, root) -> tuple[float, float]:
        """Extract width and height from SVG root element."""
        width_str = root.get('width', '24')
        height_str = root.get('height', '24')
        
        # Remove units and convert to float
        width = self._parse_dimension(width_str)
        height = self._parse_dimension(height_str)
        
        return width, height

    def _parse_dimension(self, dimension_str: str) -> float:
        """Parse dimension string removing units."""
        try:
            # Remove common units
            dimension_str = re.sub(r'(px|pt|em|rem|%)', '', dimension_str.strip())
            return float(dimension_str)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse dimension '{dimension_str}', using default 24")
            return 24.0

    def extract_viewbox(self, root) -> ViewBox:
        """Extract viewBox from SVG root element."""
        viewbox_str = root.get('viewBox')
        if viewbox_str:
            return ViewBox.from_string(viewbox_str)
        
        # Fallback to width/height if no viewBox
        width_str = root.get('width', '24')
        height_str = root.get('height', '24')
        width = self._parse_dimension(width_str)
        height = self._parse_dimension(height_str)
        
        return ViewBox(0, 0, width, height)

    def extract_paths(self, root) -> List[PathData]:
        """Extract all path and polygon elements from SVG."""
        paths = []
        
        # Extract path elements
        for path_elem in root.iter('path'):
            path_data = self._parse_path_element(path_elem)
            if path_data:
                paths.append(path_data)
        
        # Extract polygon elements and convert to paths
        for polygon_elem in root.iter('polygon'):
            path_data = self._parse_polygon_element(polygon_elem)
            if path_data:
                paths.append(path_data)
        
        # Extract polyline elements and convert to paths  
        for polyline_elem in root.iter('polyline'):
            path_data = self._parse_polyline_element(polyline_elem)
            if path_data:
                paths.append(path_data)
        
        return paths

    def _parse_path_element(self, path_elem) -> Optional[PathData]:
        """Parse a single path element."""
        d = path_elem.get('d')
        if not d:
            return None
            
        # Get style attributes - handle both direct attributes and CSS classes
        fill, stroke, stroke_width, opacity = self._extract_style_attributes(path_elem)
            
        return PathData(
            d=d.strip(),
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            fill_rule=path_elem.get('fill-rule', 'nonzero'),
            opacity=opacity,
            transform=path_elem.get('transform')
        )

    def _parse_polygon_element(self, polygon_elem) -> Optional[PathData]:
        """Parse a polygon element and convert to path data."""
        points_str = polygon_elem.get('points')
        if not points_str:
            return None
        
        try:
            # Convert polygon points to path data
            path_data = self._points_to_path_data(points_str, close_path=True)
            
            # Get style attributes
            fill, stroke, stroke_width, opacity = self._extract_style_attributes(polygon_elem)
            
            return PathData(
                d=path_data,
                fill=fill,
                stroke=stroke,
                stroke_width=stroke_width,
                fill_rule=polygon_elem.get('fill-rule', 'nonzero'),
                opacity=opacity,
                transform=polygon_elem.get('transform')
            )
        except Exception as e:
            logger.warning(f"Failed to parse polygon points '{points_str}': {e}")
            return None

    def _parse_polyline_element(self, polyline_elem) -> Optional[PathData]:
        """Parse a polyline element and convert to path data."""
        points_str = polyline_elem.get('points')
        if not points_str:
            return None
            
        try:
            # Convert polyline points to path data (no close)
            path_data = self._points_to_path_data(points_str, close_path=False)
            
            # Get style attributes
            fill, stroke, stroke_width, opacity = self._extract_style_attributes(polyline_elem)
            
            return PathData(
                d=path_data,
                fill=fill,
                stroke=stroke,
                stroke_width=stroke_width,
                fill_rule=polyline_elem.get('fill-rule', 'nonzero'),
                opacity=opacity,
                transform=polyline_elem.get('transform')
            )
        except Exception as e:
            logger.warning(f"Failed to parse polyline points '{points_str}': {e}")
            return None

    def extract_groups(self, root) -> List[GroupData]:
        """Extract all group elements from SVG."""
        groups = []
        
        for group_elem in root.iter('g'):
            group_data = self._parse_group_element(group_elem)
            groups.append(group_data)
        
        return groups

    def _parse_group_element(self, group_elem) -> GroupData:
        """Parse a single group element."""
        children = []
        
        # Parse child paths within the group
        for path_elem in group_elem.iter('path'):
            path_data = self._parse_path_element(path_elem)
            if path_data:
                children.append(path_data)
        
        return GroupData(
            transform=group_elem.get('transform'),
            opacity=float(group_elem.get('opacity', '1')),
            fill=group_elem.get('fill', 'black'),
            stroke=group_elem.get('stroke', 'none'),
            children=children
        )

    def normalize_colors(self, color: str) -> str:
        """Normalize color string to standard format."""
        return PathData._normalize_color(PathData(), color)

    def parse_path_data(self, path_string: str) -> str:
        """Parse and normalize SVG path data string."""
        # Remove extra whitespace and normalize commands
        path_string = re.sub(r'\s+', ' ', path_string.strip())
        
        # Ensure proper spacing around path commands
        path_string = re.sub(r'([MmLlHhVvCcSsQqTtAaZz])', r' \1 ', path_string)
        path_string = re.sub(r'\s+', ' ', path_string.strip())
        
        return path_string

    def _points_to_path_data(self, points_str: str, close_path: bool = True) -> str:
        """Convert SVG points string to path data."""
        # Handle both comma and space separated coordinates
        # Replace commas between coordinate pairs with spaces
        points_str = re.sub(r',', ' ', points_str.strip())
        
        # Split into coordinate pairs
        coords = []
        values = [float(x) for x in points_str.split() if x]
        
        # Group coordinates into pairs
        for i in range(0, len(values), 2):
            if i + 1 < len(values):
                coords.append((values[i], values[i + 1]))
        
        if not coords:
            return ""
        
        # Build path data string
        path_parts = [f"M {coords[0][0]} {coords[0][1]}"]
        
        for x, y in coords[1:]:
            path_parts.append(f"L {x} {y}")
        
        if close_path:
            path_parts.append("Z")
        
        return " ".join(path_parts)

    def _extract_style_attributes(self, element) -> tuple[str, str, float, float]:
        """Extract style attributes from element, handling CSS classes."""
        # Start with direct attributes
        fill = element.get('fill', 'black')
        stroke = element.get('stroke', 'none')
        stroke_width = float(element.get('stroke-width', '0'))
        opacity = float(element.get('opacity', '1'))
        
        # Handle CSS classes
        class_name = element.get('class')
        if class_name:
            # Look for style definitions in the document
            style_info = self._resolve_css_class(element, class_name)
            if style_info:
                if 'fill' in style_info:
                    fill = style_info['fill']
                if 'stroke' in style_info:
                    stroke = style_info['stroke']
                if 'stroke-width' in style_info:
                    try:
                        stroke_width = float(style_info['stroke-width'])
                    except ValueError:
                        pass
                if 'opacity' in style_info:
                    try:
                        opacity = float(style_info['opacity'])
                    except ValueError:
                        pass
        
        # Handle inline style attribute
        style_attr = element.get('style')
        if style_attr:
            style_info = self._parse_inline_style(style_attr)
            if 'fill' in style_info:
                fill = style_info['fill']
            if 'stroke' in style_info:
                stroke = style_info['stroke']
            if 'stroke-width' in style_info:
                try:
                    stroke_width = float(style_info['stroke-width'])
                except ValueError:
                    pass
            if 'opacity' in style_info:
                try:
                    opacity = float(style_info['opacity'])
                except ValueError:
                    pass
        
        return fill, stroke, stroke_width, opacity

    def _resolve_css_class(self, element, class_name: str) -> Optional[Dict[str, str]]:
        """Resolve CSS class to style properties."""
        # Find the root SVG element - traverse up the tree manually since getparent() is lxml-specific
        root = element
        
        # Since we don't have getparent() in standard ElementTree, we'll search from the document root
        # We stored the parsed tree root during parsing, so we can use that
        if hasattr(self, '_current_root'):
            root = self._current_root
        else:
            # Fallback: find root by walking up manually (limited implementation)
            # This is a simplified approach - in practice we'll use the stored root
            pass
        
        # Look for style elements
        for style_elem in root.iter('style'):
            style_text = style_elem.text or ""
            
            # Simple CSS parsing - look for .className { properties }
            class_pattern = fr'\.{re.escape(class_name)}\s*\{{([^}}]+)\}}'
            match = re.search(class_pattern, style_text)
            
            if match:
                properties_text = match.group(1)
                return self._parse_css_properties(properties_text)
        
        return None

    def _parse_css_properties(self, properties_text: str) -> Dict[str, str]:
        """Parse CSS properties from text."""
        properties = {}
        
        # Split by semicolons and parse property:value pairs
        for prop in properties_text.split(';'):
            prop = prop.strip()
            if ':' in prop:
                key, value = prop.split(':', 1)
                properties[key.strip()] = value.strip()
        
        return properties

    def _parse_inline_style(self, style_attr: str) -> Dict[str, str]:
        """Parse inline style attribute."""
        return self._parse_css_properties(style_attr)