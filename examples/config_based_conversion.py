#!/usr/bin/env python3
"""
Configuration-Based Conversion Example

This script demonstrates how to use SvgToVectorCompose with a configuration file
for repeatable, automated conversions.
"""

import os
import sys
import json
import subprocess

def create_example_config():
    """Create an example configuration file."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    config = {
        "input": os.path.join(script_dir, "input", "icons"),
        "output": os.path.join(script_dir, "output", "config_based"),
        "package": "com.myapp.icons",
        "generate_index": True,
        "iconpack_name": "MyAppIcons",
        "verbose": True,
        "clean": True
    }
    
    config_path = os.path.join(script_dir, "example_config.json")
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_path, config

def main():
    """Run configuration-based conversion example."""
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    main_script = os.path.join(project_root, "main.py")
    
    print("🎨 SvgToVectorCompose - Configuration-Based Conversion")
    print("=" * 55)
    print()
    
    # Create example configuration
    config_path, config = create_example_config()
    
    print("📋 Created configuration file:")
    print(f"   📄 {config_path}")
    print()
    print("Configuration contents:")
    print(json.dumps(config, indent=2))
    print()
    
    # Check if input directory exists
    if not os.path.exists(config["input"]):
        print(f"❌ Input directory not found: {config['input']}")
        print("Please ensure the example SVG files exist.")
        return False
    
    # Create output directory if it doesn't exist
    os.makedirs(config["output"], exist_ok=True)
    
    # Run the converter with config file
    try:
        cmd = [
            sys.executable, main_script,
            "--config", config_path
        ]
        
        print("🚀 Running conversion with config file...")
        print(f"Command: {' '.join(cmd)}")
        print()
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Conversion completed successfully!")
        print()
        print("📋 Generated files:")
        
        # List generated files
        for root, dirs, files in os.walk(config["output"]):
            for file in files:
                if file.endswith('.kt'):
                    rel_path = os.path.relpath(os.path.join(root, file), config["output"])
                    print(f"   📄 {rel_path}")
        
        print()
        print("🎯 Usage in your Compose app:")
        print("```kotlin")
        print(f"import {config['package']}.{config['iconpack_name']}")
        print()
        print("@Composable")
        print("fun MyApp() {")
        print("    // Easy access to any icon")
        print(f"    Icon(imageVector = {config['iconpack_name']}.Edit, contentDescription = \"Edit\")")
        print()
        print("    // Browse all icons")
        print("    LazyRow {")
        print(f"        items({config['iconpack_name']}.All) {{ icon ->")
        print("            Icon(imageVector = icon, contentDescription = null)")
        print("        }")
        print("    }")
        print("}")
        print("```")
        
        print()
        print("💡 Benefits of configuration files:")
        print("   • Repeatable builds")
        print("   • Version control friendly")
        print("   • Easy CI/CD integration")
        print("   • Team collaboration")
        
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