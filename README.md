# SvgToVectorCompose

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Kotlin](https://img.shields.io/badge/kotlin-multiplatform-purple.svg)
![Compose](https://img.shields.io/badge/compose-multiplatform-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**🎨 Convert SVG files to Kotlin Compose Multiplatform ImageVector code**

A powerful Python tool that transforms SVG icons into production-ready Compose Vector Drawables with perfect package structure and IconPack generation.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Examples](#examples) • [Contributing](#contributing)

</div>

---

## 🌟 Features

- **🎯 High Success Rate**: 100% conversion success on complex SVG icons (tested on 8,000+ IntelliJ icons)
- **🔄 Batch Processing**: Convert entire directories of SVG files while preserving folder structure
- **📦 Smart Package Management**: Auto-generates proper Kotlin package names from directory structure
- **🏗️ IconPack Generation**: Creates convenient IconPack objects for easy icon access (`MyIcons.ArrowLeft`)
- **🎨 Intelligent Naming**: Converts filenames to PascalCase with Kotlin keyword protection
- **📊 Real-time Progress**: Live conversion progress with detailed logging
- **⚙️ Flexible Configuration**: CLI arguments, interactive mode, or JSON config files
- **🔧 Production Ready**: Generates proper Kotlin Multiplatform compatible code

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/xcodebn/SvgToVectorCompose.git
cd SvgToVectorCompose
pip install -r requirements.txt
```

### Basic Usage

```bash
# Interactive mode (recommended for first-time users)
python main.py --interactive

# Direct conversion
python main.py -i ./svg_icons -o ./compose_icons -p com.myapp.icons --generate-index

# With custom IconPack name
python main.py -i ./icons -o ./output -p com.app.icons --generate-index --iconpack-name "AppIcons"
```

## 📖 Detailed Usage

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  -i, --input PATH              Input directory containing SVG files
  -o, --output PATH             Output directory for generated Kotlin files
  -p, --package PACKAGE         Package name for generated Kotlin files
  --generate-index              Generate IconPack file for easy icon access
  --iconpack-name NAME          Custom name for IconPack object (default: Icons)
  --clean                       Clean output directory before conversion
  --dry-run                     Preview conversion without writing files
  --verbose                     Enable detailed logging
  --interactive                 Interactive mode with guided setup
  --config CONFIG               Load configuration from JSON file
```

### Configuration File

Create a `config.json` file for repeated usage:

```json
{
    "input": "./svg_icons",
    "output": "./compose_icons",
    "package": "com.myapp.icons",
    "generate_index": true,
    "iconpack_name": "MyIcons",
    "verbose": false,
    "clean": true
}
```

Then run: `python main.py --config config.json`

## 💡 Examples

### Quick Examples

Try the included examples to see SvgToVectorCompose in action:

```bash
# Run basic conversion example
cd examples
python basic_conversion.py

# Try configuration-based conversion
python config_based_conversion.py

# Launch interactive demo
python interactive_demo.py
```

See the [examples directory](examples/README.md) for detailed demonstrations and sample code.

### Input Structure
```
svg_icons/
├── actions/
│   ├── edit.svg
│   ├── delete.svg
│   └── save.svg
├── navigation/
│   ├── arrow-left.svg
│   └── home.svg
└── logo.svg
```

### Generated Output
```
compose_icons/
├── MyIcons.kt                    # IconPack file
├── actions/
│   ├── Edit.kt
│   ├── Delete.kt
│   └── Save.kt
├── navigation/
│   ├── ArrowLeft.kt
│   └── Home.kt
└── Logo.kt
```

### Generated IconPack Usage

```kotlin
import com.myapp.icons.MyIcons

@Composable
fun MyApp() {
    // Easy access to any icon
    Icon(
        imageVector = MyIcons.ArrowLeft,
        contentDescription = "Navigate back"
    )
    
    // Browse all icons
    LazyRow {
        items(MyIcons.All) { icon ->
            Icon(imageVector = icon, contentDescription = null)
        }
    }
    
    // Dynamic icon access
    val icon = MyIcons.getByName("Edit")
    if (icon != null) {
        Icon(imageVector = icon, contentDescription = "Edit")
    }
}
```

### Individual Icon Usage

```kotlin
import com.myapp.icons.actions.Edit
import com.myapp.icons.navigation.ArrowLeft

@Composable
fun Toolbar() {
    IconButton(onClick = { /* edit action */ }) {
        Icon(imageVector = Edit, contentDescription = "Edit")
    }
    
    IconButton(onClick = { /* back action */ }) {
        Icon(imageVector = ArrowLeft, contentDescription = "Back")
    }
}
```

## 🏗️ Real-World Example: IntelliJ Icons Library

This tool was used to create a complete IntelliJ Icons library for Compose Multiplatform:

```bash
# Convert 8,000+ IntelliJ icons
python main.py \
  -i "/path/to/intellij-icons" \
  -o "./IntellijIconsLibrary" \
  -p "com.github.xcodebn.intellijicons" \
  --generate-index \
  --iconpack-name "IntellijIcons" \
  --clean
```

**Result**: 8,080 perfectly converted Kotlin files with 100% success rate!

## 🔧 Advanced Features

### Smart File Naming

The converter intelligently handles edge cases:

```bash
# Input filename        → Output filename     → Variable name
arrow-left.svg         → ArrowLeft.kt        → ArrowLeft
123icon.svg           → Icon123icon.kt      → Icon123icon  
class.svg             → ClassIcon.kt        → ClassIcon
icon@2x.svg           → Icon2x.kt           → Icon2x
multi-word-icon.svg   → MultiWordIcon.kt    → MultiWordIcon
```

### Package Structure

Directory structure is preserved in package names:

```bash
# Directory: icons/actions/edit.svg
# Package: com.myapp.icons.actions
# File: icons/actions/Edit.kt
```

### Complex SVG Support

Handles advanced SVG features:
- ✅ Path elements with complex commands
- ✅ Polygon and polyline elements  
- ✅ CSS class styles and inline styles
- ✅ Nested groups and transformations
- ✅ Multiple color formats (hex, named, rgb)
- ✅ ViewBox and dimension handling


## 🛠️ Development

### Project Structure

```
SvgToVectorCompose/
├── main.py                      # CLI entry point
├── converter/                   # Core conversion logic
│   ├── __init__.py             # Package initialization
│   ├── svg_parser.py           # SVG parsing with advanced features
│   ├── compose_generator.py    # Kotlin code generation
│   └── file_processor.py       # File operations and IconPack generation
├── examples/                    # Usage examples and demos
│   ├── README.md               # Examples documentation
│   ├── input/icons/            # Sample SVG files
│   ├── basic_conversion.py     # Basic usage example
│   ├── config_based_conversion.py # Config file example
│   └── interactive_demo.py     # Interactive mode demo
├── templates/                   # Kotlin code templates
│   └── compose_template.kt     # Template for generated Kotlin files
├── .github/workflows/          # GitHub Actions CI/CD
│   └── test.yml               # Automated testing workflow
├── config.example.json         # Example configuration file
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── CONTRIBUTING.md             # Contribution guidelines
├── README.md                   # This file
└── LICENSE                     # MIT license
```

### Getting Started

```bash
# Clone the repository
git clone https://github.com/xcodebn/SvgToVectorCompose.git
cd SvgToVectorCompose

# Install dependencies
pip install -r requirements.txt

# Run the converter
python main.py --interactive
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Contribution Ideas

- 🐛 **Bug fixes**: Report and fix conversion issues
- 🎨 **New features**: SVG filters, animations support
- 📖 **Documentation**: Improve guides and examples
- 🧪 **Testing**: Add test frameworks and edge cases
- 🚀 **Performance**: Optimize conversion speed

## 📝 Changelog

### v1.0.0 (Latest)
- ✨ Complete SVG to Compose conversion
- 🎯 IconPack generation with customizable names
- 📦 Proper package structure from directory hierarchy
- 🎨 Smart filename normalization
- 🔧 Interactive mode and config file support
- 📊 Real-time progress tracking
- 🧪 100% success rate on complex icon sets

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **JetBrains** for the amazing IntelliJ icons used in testing
- **Google** for Compose Multiplatform
- **Material Design** for icon design inspiration
- **Python community** for excellent XML and file processing libraries

---

<div align="center">

**Made with ❤️ by [xcodebn](https://github.com/xcodebn)**

⭐ **Star this repo if it helped you!** ⭐

[Report Bug](https://github.com/xcodebn/SvgToVectorCompose/issues) • [Request Feature](https://github.com/xcodebn/SvgToVectorCompose/issues) • [Discussion](https://github.com/xcodebn/SvgToVectorCompose/discussions)

</div>