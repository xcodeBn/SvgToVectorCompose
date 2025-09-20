#!/usr/bin/env python3
"""
Interactive Demo

This script demonstrates the interactive mode of SvgToVectorCompose,
which guides users through the conversion process step by step.
"""

import os
import sys
import subprocess

def main():
    """Run interactive demo."""
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    main_script = os.path.join(project_root, "main.py")
    
    print("🎨 SvgToVectorCompose - Interactive Demo")
    print("=" * 40)
    print()
    print("This demo will launch the interactive mode of SvgToVectorCompose.")
    print("The interactive mode guides you through:")
    print()
    print("   📁 Selecting input directory")
    print("   📁 Choosing output directory")
    print("   📦 Setting package name")
    print("   🏷️  Configuring IconPack name")
    print("   ⚙️  Choosing additional options")
    print()
    print("Perfect for:")
    print("   👤 First-time users")
    print("   🔍 Exploring options")
    print("   🧪 Quick experiments")
    print()
    
    # Show example input directory
    input_dir = os.path.join(script_dir, "input", "icons")
    if os.path.exists(input_dir):
        print(f"💡 Tip: You can use the example icons at:")
        print(f"   {input_dir}")
        print()
    
    input("Press Enter to launch interactive mode...")
    print()
    
    # Run the converter in interactive mode
    try:
        cmd = [sys.executable, main_script, "--interactive"]
        
        print("🚀 Launching interactive mode...")
        print()
        
        # Run interactively (no capture, let user interact)
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print()
            print("✅ Interactive session completed!")
            print()
            print("🎯 Next Steps:")
            print("   • Check your output directory for generated files")
            print("   • Import the IconPack in your Compose project")
            print("   • Use individual icons or browse all icons")
            print("   • Create a config file for automation")
        else:
            print()
            print("❌ Interactive session ended with errors.")
            print("Please check the output above for details.")
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print()
        print("⏹️  Interactive session cancelled by user.")
        return True
    
    except Exception as e:
        print(f"❌ Error launching interactive mode: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)