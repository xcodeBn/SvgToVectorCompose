"""Main entry point for SVG to Compose Vector Drawable converter."""

import argparse
import logging
import sys
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from converter import SVGParser, ComposeGenerator, FileProcessor, ConversionReport


@dataclass
class ConverterConfig:
    """Configuration for the SVG converter."""
    input_dir: Path
    output_dir: Path
    package_name: str
    verbose: bool = False
    dry_run: bool = False
    clean_output: bool = False
    generate_index: bool = False
    iconpack_name: str = "Icons"


class SVGToComposeConverter:
    """Main converter class that orchestrates the conversion process."""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
        self.parser = SVGParser()
        self.generator = ComposeGenerator(config.package_name)
        self.file_processor = FileProcessor(config.input_dir, config.output_dir)
        
        # Setup logging
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)

    def _setup_logging(self):
        """Setup logging configuration."""
        level = logging.DEBUG if self.config.verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )

    def convert_all(self) -> ConversionReport:
        """Convert all SVG files in the input directory."""
        self.logger.info(f"Starting conversion from {self.config.input_dir} to {self.config.output_dir}")
        self.logger.info(f"Package name: {self.config.package_name}")
        
        # Clean output directory if requested
        if self.config.clean_output and not self.config.dry_run:
            self.logger.info("Cleaning output directory...")
            self.file_processor.clean_output_directory(confirm=True)
        
        # Scan for SVG files
        svg_files = self.file_processor.scan_directory()
        
        if not svg_files:
            self.logger.warning("No SVG files found in input directory")
            return ConversionReport(0, 0, 0, ["No SVG files found"], [])
        
        # Initialize report
        report = ConversionReport(
            total_files=len(svg_files),
            successful_conversions=0,
            failed_conversions=0,
            errors=[],
            output_files=[]
        )
        
        # Process each SVG file
        for i, svg_path in enumerate(svg_files, 1):
            progress_percent = (i / len(svg_files)) * 100
            
            if not self.config.verbose:
                # Simple progress for non-verbose mode
                print(f"\r🔄 Converting: {i}/{len(svg_files)} ({progress_percent:.1f}%) - {svg_path.name[:50]}{'...' if len(svg_path.name) > 50 else ''}", end='', flush=True)
            else:
                self.logger.info(f"Processing {svg_path.name} ({i}/{len(svg_files)} - {progress_percent:.1f}%)")
            
            try:
                success = self.convert_single_file(svg_path)
                
                if success:
                    report.successful_conversions += 1
                    output_path = self.file_processor.get_output_path(svg_path)
                    report.output_files.append(output_path)
                    if self.config.verbose:
                        self.logger.info(f"✓ Successfully converted {svg_path.name}")
                else:
                    report.failed_conversions += 1
                    error_msg = f"Failed to convert {svg_path.name}"
                    report.errors.append(error_msg)
                    if self.config.verbose:
                        self.logger.error(f"✗ {error_msg}")
                    
            except Exception as e:
                report.failed_conversions += 1
                error_msg = f"Error converting {svg_path.name}: {str(e)}"
                report.errors.append(error_msg)
                if self.config.verbose:
                    self.logger.error(f"✗ {error_msg}")
        
        # Clear progress line if not verbose
        if not self.config.verbose:
            print("\r" + " " * 100 + "\r", end='', flush=True)
        
        # Print summary
        self._print_summary(report)
        
        return report

    def convert_single_file(self, svg_path: Path) -> bool:
        """Convert a single SVG file to Compose ImageVector."""
        try:
            # Parse SVG file
            self.logger.debug(f"Parsing SVG file: {svg_path}")
            svg_data = self.parser.parse_svg_file(svg_path)
            
            # Generate class name from filename
            class_name = svg_path.stem
            
            # Get relative path from input directory for package structure
            relative_path = svg_path.relative_to(self.config.input_dir)
            
            # Generate Kotlin code
            self.logger.debug(f"Generating Kotlin code for: {class_name}")
            kotlin_code = self.generator.generate_vector_drawable(svg_data, class_name, str(relative_path))
            
            if self.config.dry_run:
                self.logger.info(f"DRY RUN: Would generate {class_name}.kt")
                self.logger.debug("Generated code preview:")
                self.logger.debug(kotlin_code[:500] + "..." if len(kotlin_code) > 500 else kotlin_code)
                return True
            
            # Determine output path
            output_path = self.file_processor.get_output_path(svg_path)
            
            # Create output directory structure
            self.file_processor.create_output_structure(svg_path)
            
            # Write Kotlin file
            success = self.file_processor.write_kotlin_file(kotlin_code, output_path)
            
            if success:
                self.logger.debug(f"Written Kotlin file: {output_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error converting {svg_path}: {e}")
            return False

    def generate_iconpack_file(self) -> Optional[Path]:
        """Generate an IconPack file with easy access to all icons."""
        try:
            output_files = self.file_processor.list_output_files()
            
            if not output_files:
                self.logger.warning("No output files found for IconPack generation")
                return None
            
            # Generate IconPack content
            iconpack_content = self._generate_iconpack_content(output_files)
            
            # Write IconPack file with custom name
            iconpack_filename = f"{self.config.iconpack_name}.kt"
            iconpack_path = self.config.output_dir / iconpack_filename
            
            if self.config.dry_run:
                self.logger.info(f"DRY RUN: Would generate IconPack file at {iconpack_path}")
                return iconpack_path
            
            success = self.file_processor.write_kotlin_file(iconpack_content, iconpack_path)
            
            if success:
                self.logger.info(f"Generated IconPack file: {iconpack_path}")
                return iconpack_path
            else:
                self.logger.error("Failed to write IconPack file")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating IconPack file: {e}")
            return None

    def _generate_iconpack_content(self, output_files: list[Path]) -> str:
        """Generate content for the IconPack file."""
        icon_data = []
        
        for file_path in output_files:
            # Extract the original SVG filename to get the proper variable name
            # We need to read the actual variable name from the generated file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Find the variable name: look for "val VariableName: ImageVector"
                    import re
                    match = re.search(r'val (\w+): ImageVector', content)
                    if match:
                        actual_variable_name = match.group(1)
                    else:
                        # Fallback to filename if pattern not found
                        actual_variable_name = file_path.stem
            except Exception:
                # Fallback to filename if reading fails
                actual_variable_name = file_path.stem
            
            # Store relative path for nested structure
            relative_path = file_path.relative_to(self.config.output_dir)
            icon_data.append({
                'name': actual_variable_name,
                'path': relative_path,
                'variable_name': actual_variable_name
            })
        
        # Sort by icon name
        icon_data.sort(key=lambda x: x['name'])
        
        # Handle duplicate names by adding directory suffix
        icon_data = self._resolve_duplicate_names(icon_data)
        
        # No imports needed since we're using fully qualified names
        
        # Generate individual icon properties using fully qualified names to avoid loops
        icon_properties = []
        for icon in icon_data:
            # Build full package name including directory structure
            icon_package = self.generator._build_package_name(str(icon['path']))
            icon_properties.append(f"    val {icon['name']}: ImageVector get() = {icon_package}.{icon['variable_name']}")
        
        # Generate icon list using fully qualified names
        icon_list_items = []
        for icon in icon_data:
            icon_package = self.generator._build_package_name(str(icon['path']))
            icon_list_items.append(f"{icon_package}.{icon['variable_name']}")
        
        # Generate when clauses for getByName function using fully qualified names
        when_clauses = []
        for icon in icon_data:
            icon_package = self.generator._build_package_name(str(icon['path']))
            when_clauses.append(f'        "{icon["name"]}" -> {icon_package}.{icon["variable_name"]}')
        
        # Build the content string step by step to avoid f-string issues
        header = f"""package {self.config.package_name}

import androidx.compose.ui.graphics.vector.ImageVector

/**
 * IconPack containing all converted SVG icons.
 * 
 * Usage:
 * ```kotlin
 * Icon(imageVector = {self.config.iconpack_name}.ArrowLeft, contentDescription = "Arrow Left")
 * ```
 */
object {self.config.iconpack_name} {{"""

        properties_section = chr(10).join(icon_properties)
        
        icon_list_formatted = ',\n        '.join(icon_list_items)
        list_section = f"""    
    /**
     * List of all icons in this pack.
     */
    val All: List<ImageVector> = listOf(
        {icon_list_formatted}
    )
    
    /**
     * Total number of icons in this pack.
     */
    val Count: Int = All.size"""

        when_clauses_formatted = chr(10).join(when_clauses)
        function_section = f"""    
    /**
     * Get icon by name (case-sensitive).
     */
    fun getByName(name: String): ImageVector? = when (name) {{
{when_clauses_formatted}
        else -> null
    }}
}}"""

        iconpack_content = header + chr(10) + properties_section + list_section + function_section
        return iconpack_content

    def _resolve_duplicate_names(self, icon_data: list) -> list:
        """Resolve duplicate icon names by adding directory suffix."""
        # Group icons by name to find duplicates
        name_groups = {}
        for icon in icon_data:
            name = icon['name']
            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append(icon)
        
        # Process each group
        resolved_icons = []
        for name, icons in name_groups.items():
            if len(icons) == 1:
                # No duplicates, keep original
                resolved_icons.append(icons[0])
            else:
                # Handle duplicates by adding directory suffix
                for icon in icons:
                    # Get the immediate parent directory name
                    path_parts = icon['path'].parts
                    if len(path_parts) > 1:
                        # Get the directory name (second to last part, since last is filename)
                        dir_name = path_parts[-2]
                        # Capitalize first letter for consistent naming
                        dir_suffix = dir_name.capitalize()
                        new_name = f"{name}{dir_suffix}"
                    else:
                        # Fallback if no directory
                        new_name = f"{name}Root"
                    
                    # Update the icon data
                    icon['name'] = new_name
                    resolved_icons.append(icon)
        
        return resolved_icons

    def _print_summary(self, report: ConversionReport):
        """Print conversion summary."""
        self.logger.info("=" * 50)
        self.logger.info("CONVERSION SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total files processed: {report.total_files}")
        self.logger.info(f"Successful conversions: {report.successful_conversions}")
        self.logger.info(f"Failed conversions: {report.failed_conversions}")
        self.logger.info(f"Success rate: {report.success_rate:.1f}%")
        
        if report.errors:
            self.logger.info("\nErrors:")
            for error in report.errors:
                self.logger.info(f"  - {error}")
        
        if report.output_files and not self.config.dry_run:
            self.logger.info(f"\nGenerated {len(report.output_files)} Kotlin files in {self.config.output_dir}")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="🎨 SVG to Compose Vector Drawable Converter",
        epilog="""
📖 Examples:
  %(prog)s -i ./svg_icons -o ./compose_icons -p com.myapp.icons
  %(prog)s -i ./icons -o ./output --verbose --dry-run  
  %(prog)s -i ./svg -o ./kotlin -p com.example.icons --clean --generate-index
  %(prog)s --interactive  # Interactive mode for easy setup

🔧 Tips:
  • Use --dry-run to preview conversion without writing files
  • Use --verbose for detailed progress information  
  • Package names with dashes will be automatically normalized (my-app → my_app)
  • Icon names are converted to PascalCase (arrow-right → ArrowRight)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--input',
        type=Path,
        help='Input directory containing SVG files'
    )
    
    parser.add_argument(
        '-o', '--output', 
        type=Path,
        help='Output directory for generated Kotlin files'
    )
    
    parser.add_argument(
        '-p', '--package',
        type=str,
        default='com.example.icons',
        help='Package name for generated Kotlin files (default: com.example.icons)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview conversion without writing files'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean output directory before conversion'
    )
    
    parser.add_argument(
        '--generate-index',
        action='store_true',
        help='Generate IconPack file for easy icon access'
    )
    
    parser.add_argument(
        '--iconpack-name',
        type=str,
        default='Icons',
        help='Name for the generated IconPack object (default: Icons)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode with prompts'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Load configuration from file'
    )
    
    return parser


def validate_args(args: argparse.Namespace) -> ConverterConfig:
    """Validate command line arguments and create config."""
    # Check if required arguments are provided (not needed for interactive mode)
    if not args.interactive:
        if not args.input:
            raise ValueError("Input directory is required (use -i/--input or --interactive)")
        if not args.output:
            raise ValueError("Output directory is required (use -o/--output or --interactive)")
    
    # Validate input directory
    if args.input and not args.input.exists():
        raise FileNotFoundError(f"Input directory does not exist: {args.input}")
    
    if args.input and not args.input.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {args.input}")
    
    # Normalize package name - replace dashes with underscores and validate
    package = args.package or "com.example.icons"
    normalized_package = normalize_package_name(package)
    
    # Validate normalized package name
    package_pattern = r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$'
    if not re.match(package_pattern, normalized_package):
        raise ValueError(f"Invalid package name: {normalized_package} (normalized from {package})")
    
    # Create output directory if it doesn't exist
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
    
    return ConverterConfig(
        input_dir=args.input.resolve() if args.input else None,
        output_dir=args.output.resolve() if args.output else None,
        package_name=normalized_package,
        verbose=args.verbose or False,
        dry_run=args.dry_run or False,
        clean_output=args.clean or False,
        generate_index=args.generate_index or False,
        iconpack_name=args.iconpack_name or "Icons"
    )


def normalize_package_name(package_name: str) -> str:
    """Normalize package name to be valid for Kotlin/Java."""
    # Replace dashes with underscores
    normalized = package_name.replace('-', '_')
    
    # Ensure each part starts with lowercase and contains only valid characters
    parts = normalized.split('.')
    normalized_parts = []
    
    for part in parts:
        # Remove invalid characters and ensure it starts with a letter
        clean_part = re.sub(r'[^a-zA-Z0-9_]', '', part.lower())
        if clean_part and not clean_part[0].isalpha():
            clean_part = 'pkg_' + clean_part
        if clean_part:
            normalized_parts.append(clean_part)
    
    return '.'.join(normalized_parts) if normalized_parts else 'com.example.icons'


def interactive_mode() -> ConverterConfig:
    """Run in interactive mode to collect user input."""
    print("🎨 SVG to Compose Vector Drawable Converter")
    print("=" * 50)
    
    # Get input directory
    while True:
        input_dir = input("\n📁 Enter path to SVG files directory: ").strip()
        if not input_dir:
            print("❌ Input directory is required")
            continue
        
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ Directory does not exist: {input_path}")
            continue
        if not input_path.is_dir():
            print(f"❌ Path is not a directory: {input_path}")
            continue
        
        # Count SVG files
        svg_count = len(list(input_path.rglob("*.svg")))
        print(f"✅ Found {svg_count} SVG files")
        if svg_count == 0:
            print("⚠️  No SVG files found, but continuing...")
        break
    
    # Get output directory
    while True:
        output_dir = input("\n📁 Enter output directory for Kotlin files: ").strip()
        if not output_dir:
            print("❌ Output directory is required")
            continue
        
        output_path = Path(output_dir)
        if output_path.exists() and any(output_path.iterdir()):
            response = input(f"⚠️  Directory {output_path} exists and is not empty. Continue? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                continue
        break
    
    # Get package name
    while True:
        package_name = input("\n📦 Enter package name (e.g., com.myapp.icons): ").strip()
        if not package_name:
            package_name = "com.example.icons"
            print(f"✅ Using default: {package_name}")
            break
        
        try:
            normalized = normalize_package_name(package_name)
            if normalized != package_name:
                print(f"📝 Normalized package name: {normalized}")
            package_name = normalized
            break
        except Exception as e:
            print(f"❌ Invalid package name: {e}")
    
    # Options
    print("\n⚙️  Options:")
    verbose = input("   Enable verbose logging? (y/N): ").strip().lower() in ['y', 'yes']
    clean_output = input("   Clean output directory before conversion? (y/N): ").strip().lower() in ['y', 'yes']
    generate_index = input("   Generate IconPack file for easy icon access? (y/N): ").strip().lower() in ['y', 'yes']
    
    iconpack_name = "Icons"
    if generate_index:
        custom_name = input("   IconPack name (default: Icons): ").strip()
        if custom_name:
            iconpack_name = custom_name
    
    dry_run = input("   Dry run (preview without writing files)? (y/N): ").strip().lower() in ['y', 'yes']
    
    # Summary
    print("\n📋 Summary:")
    print(f"   Input:  {input_path}")
    print(f"   Output: {output_path}")
    print(f"   Package: {package_name}")
    iconpack_info = f"IconPack={iconpack_name}" if generate_index else "no IconPack"
    print(f"   Options: verbose={verbose}, clean={clean_output}, {iconpack_info}, dry_run={dry_run}")
    
    response = input("\n🚀 Start conversion? (Y/n): ").strip().lower()
    if response in ['n', 'no']:
        print("❌ Conversion cancelled")
        sys.exit(0)
    
    return ConverterConfig(
        input_dir=input_path.resolve(),
        output_dir=output_path.resolve(),
        package_name=package_name,
        verbose=verbose,
        dry_run=dry_run,
        clean_output=clean_output,
        generate_index=generate_index,
        iconpack_name=iconpack_name
    )


def load_config_file(config_path: Path) -> dict:
    """Load configuration from file."""
    try:
        import json
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config file: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        # Parse command line arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Handle interactive mode
        if args.interactive:
            config = interactive_mode()
        else:
            # Handle config file
            if args.config:
                config_data = load_config_file(args.config)
                # Override args with config file values
                for key, value in config_data.items():
                    if hasattr(args, key) and value is not None:
                        setattr(args, key, value)
            
            # Validate arguments and create config
            config = validate_args(args)
        
        # Create and run converter
        converter = SVGToComposeConverter(config)
        
        print(f"\n🎨 Starting conversion...")
        print(f"📁 Input:  {config.input_dir}")
        print(f"📁 Output: {config.output_dir}")
        print(f"📦 Package: {config.package_name}")
        
        report = converter.convert_all()
        
        # Generate IconPack file if requested
        if config.generate_index and report.successful_conversions > 0:
            print(f"\n📑 Generating IconPack file...")
            converter.generate_iconpack_file()
        
        # Final success message
        if report.successful_conversions > 0:
            print(f"\n🎉 Success! Generated {report.successful_conversions} Kotlin files")
            if not config.dry_run:
                print(f"📂 Files saved to: {config.output_dir}")
        
        # Exit with appropriate code
        if report.failed_conversions > 0:
            sys.exit(1)
        elif report.successful_conversions == 0:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n❌ Conversion cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()