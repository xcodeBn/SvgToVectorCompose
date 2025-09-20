# SVG to Compose Converter

**🎨 Convert SVG files to Kotlin Compose ImageVector code**

A simple Python tool that transforms SVG icons into Compose Vector Drawables with proper package structure and IconPack generation.

---

## 🚀 Quick Start

**1. Clone and install:**
```bash
git clone https://github.com/xcodebn/SvgToVectorCompose.git
cd SvgToVectorCompose
pip install -r requirements.txt
```

**2. Convert your SVGs:**
```bash
python main.py -i ./svg_icons -o ./compose_icons -p com.myapp.icons --generate-index
```

**3. Use in your Compose project:**
```kotlin
Icon(imageVector = MyIcons.ArrowLeft, contentDescription = "Back")
```

### Command Line Options

```bash
python main.py [OPTIONS]

Required:
  -i, --input PATH              Input directory containing SVG files
  -o, --output PATH             Output directory for generated Kotlin files
  -p, --package PACKAGE         Package name (e.g., com.myapp.icons)

Optional:
  --generate-index              Generate IconPack file for easy access
  --iconpack-name NAME          Custom IconPack name (default: Icons)  
  --verbose                     Show detailed conversion progress
  --clean                       Clean output directory first
  --interactive                 Interactive mode for beginners
```

### Examples

**Basic conversion:**
```bash
python main.py -i ./icons -o ./output -p com.app.icons
```

**With IconPack generation:**
```bash
python main.py -i ./icons -o ./output -p com.app.icons --generate-index --iconpack-name "AppIcons"
```

**Interactive mode:**
```bash
python main.py --interactive
```

## 📁 File Structure

**Input:**
```
svg_icons/
├── actions/
│   ├── edit.svg
│   └── delete.svg
├── navigation/
│   └── arrow-left.svg
└── logo.svg
```

**Generated Output:**
```
compose_icons/
├── MyIcons.kt                    # IconPack (if --generate-index used)
├── actions/
│   ├── Edit.kt
│   └── Delete.kt
├── navigation/
│   └── ArrowLeft.kt
└── Logo.kt
```

## 🎯 Using Generated Icons

**With IconPack:**
```kotlin
// Easy access to any icon
Icon(imageVector = MyIcons.ArrowLeft, contentDescription = "Back")

// Browse all available icons  
LazyRow {
    items(MyIcons.All) { icon ->
        Icon(imageVector = icon, contentDescription = null)
    }
}

// Get icon by name
val editIcon = MyIcons.getByName("Edit")
```

**Direct imports:**
```kotlin
import com.myapp.icons.actions.Edit
import com.myapp.icons.navigation.ArrowLeft

Icon(imageVector = Edit, contentDescription = "Edit")
Icon(imageVector = ArrowLeft, contentDescription = "Back")
```

## ⚠️ Important Notes

**Large SVG Files:**
Some very complex SVG files with thousands of path commands may cause JVM method size limit errors during compilation. If you encounter "Method too large" errors, consider:
- Simplifying the SVG in a graphics editor
- Splitting complex icons into multiple simpler icons
- Excluding problematic files from conversion

**File Naming:**
- Files are converted to PascalCase: `arrow-left.svg` → `ArrowLeft.kt`
- Numbers at start get "Icon" prefix: `123icon.svg` → `Icon123icon.kt`
- Directory names become package names: `actions/` → `com.app.icons.actions`

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the Compose community**