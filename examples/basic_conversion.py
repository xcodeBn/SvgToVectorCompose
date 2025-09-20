#!/usr/bin/env python3
"""
Basic Conversion Example

This script demonstrates how to use SvgToVectorCompose for basic icon conversion.
It converts the example SVG icons to Kotlin Compose ImageVectors.
"""

import os
import sys
import subprocess

def main():
    """Run basic conversion example."""
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Define paths
    input_dir = os.path.join(script_dir, "input", "icons")
    output_dir = os.path.join(script_dir, "output", "basic")
    main_script = os.path.join(project_root, "main.py")
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        print("Please ensure the example SVG files exist.")
        return False
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 SvgToVectorCompose - Basic Conversion Example")
    print("=" * 50)
    print(f"📁 Input:  {input_dir}")
    print(f"📁 Output: {output_dir}")
    print()
    
    # Run the converter
    try:
        cmd = [
            sys.executable, main_script,
            "--input", input_dir,
            "--output", output_dir,
            "--package", "com.example.icons",
            "--generate-index",
            "--iconpack-name", "ExampleIcons",
            "--verbose",
            "--clean"
        ]
        
        print("🚀 Running conversion...")
        print(f"Command: {' '.join(cmd)}")
        print()
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Conversion completed successfully!")
        print()
        print("📋 Generated files:")
        
        # List generated files
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.kt'):
                    rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                    print(f"   📄 {rel_path}")
        
        print()
        print("🎯 Usage in your Compose app:")
        print("```kotlin")
        print("import com.example.icons.ExampleIcons")
        print()
        print("@Composable")
        print("fun MyApp() {")
        print("    Icon(")
        print("        imageVector = ExampleIcons.Edit,")
        print("        contentDescription = \"Edit\"")
        print("    )")
        print("}")
        print("```")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)