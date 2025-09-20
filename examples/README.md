# Examples

This directory contains examples demonstrating different ways to use SvgToVectorCompose.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file
├── input/                       # Sample SVG files
│   └── icons/
│       ├── actions/
│       │   ├── edit.svg
│       │   └── delete.svg
│       └── navigation/
│           ├── arrow-left.svg
│           └── home.svg
├── basic_conversion.py          # Simple conversion example
├── config_based_conversion.py   # Configuration file example
└── interactive_demo.py          # Interactive mode demo
```

## 🚀 Running Examples

### 1. Basic Conversion

Demonstrates simple command-line usage:

```bash
cd examples
python basic_conversion.py
```

**What it does:**
- Converts sample SVG icons to Kotlin files
- Creates an IconPack named "ExampleIcons"
- Shows generated file structure
- Provides usage examples

### 2. Configuration-Based Conversion

Shows how to use configuration files for repeatable builds:

```bash
cd examples
python config_based_conversion.py
```

**What it does:**
- Creates an example configuration file
- Runs conversion using the config file
- Demonstrates automation benefits
- Shows CI/CD integration possibilities

### 3. Interactive Demo

Launches the guided interactive mode:

```bash
cd examples
python interactive_demo.py
```

**What it does:**
- Starts the interactive CLI
- Guides you through all options
- Perfect for first-time users
- Allows experimentation

## 📋 Sample Output

After running the examples, you'll get Kotlin files like:

### IconPack File (`ExampleIcons.kt`)
```kotlin
package com.example.icons

import androidx.compose.ui.graphics.vector.ImageVector
import com.example.icons.actions.Delete
import com.example.icons.actions.Edit
import com.example.icons.navigation.ArrowLeft
import com.example.icons.navigation.Home

object ExampleIcons {
    val Delete: ImageVector = Delete
    val Edit: ImageVector = Edit
    val ArrowLeft: ImageVector = ArrowLeft
    val Home: ImageVector = Home
    
    val All: List<ImageVector> = listOf(Delete, Edit, ArrowLeft, Home)
    val Count: Int = All.size
    
    fun getByName(name: String): ImageVector? = when (name) {
        "Delete" -> Delete
        "Edit" -> Edit
        "ArrowLeft" -> ArrowLeft
        "Home" -> Home
        else -> null
    }
}
```

### Individual Icon File (`actions/Edit.kt`)
```kotlin
package com.example.icons.actions

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathFillType.Companion.NonZero
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap.Companion.Butt
import androidx.compose.ui.graphics.StrokeJoin.Companion.Miter
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.ImageVector.Builder
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

val Edit: ImageVector
    get() {
        if (_edit != null) {
            return _edit!!
        }
        _edit = Builder(
            name = "Edit", 
            defaultWidth = 24.0.dp, 
            defaultHeight = 24.0.dp, 
            viewportWidth = 24.0f, 
            viewportHeight = 24.0f
        ).apply {
            path(
                fill = SolidColor(Color(0xFF000000)), 
                stroke = null, 
                strokeLineWidth = 0.0f, 
                strokeLineCap = Butt, 
                strokeLineJoin = Miter, 
                strokeLineMiter = 4.0f, 
                pathFillType = NonZero
            ) {
                moveTo(3.0f, 17.25f)
                verticalLineTo(21.0f)
                horizontalLineToRelative(3.75f)
                lineTo(17.81f, 9.94f)
                lineToRelative(-3.75f, -3.75f)
                lineTo(3.0f, 17.25f)
                close()
                moveTo(20.71f, 7.04f)
                curveToRelative(0.39f, -0.39f, 0.39f, -1.02f, 0.0f, -1.41f)
                lineToRelative(-2.34f, -2.34f)
                curveToRelative(-0.39f, -0.39f, -1.02f, -0.39f, -1.41f, 0.0f)
                lineToRelative(-1.83f, 1.83f)
                lineToRelative(3.75f, 3.75f)
                lineToRelative(1.83f, -1.83f)
                close()
            }
        }.build()
        return _edit!!
    }

private var _edit: ImageVector? = null
```

## 🎯 Usage in Compose

```kotlin
@Composable
fun MyApp() {
    // Using IconPack
    Icon(
        imageVector = ExampleIcons.Edit,
        contentDescription = "Edit"
    )
    
    // Browse all icons
    LazyRow {
        items(ExampleIcons.All) { icon ->
            Icon(
                imageVector = icon,
                contentDescription = null
            )
        }
    }
    
    // Dynamic access
    val iconName = "Delete"
    ExampleIcons.getByName(iconName)?.let { icon ->
        Icon(
            imageVector = icon,
            contentDescription = iconName
        )
    }
}
```

## 🛠️ Customization

### Modify Package Names

Edit the example scripts to change package names:

```python
cmd = [
    sys.executable, main_script,
    "--package", "your.custom.package",  # Change this
    "--iconpack-name", "YourIcons",      # And this
    # ... other options
]
```

### Add Your Own SVGs

1. Replace files in `input/icons/` with your SVG files
2. Run any of the example scripts
3. Generated Kotlin files will use your icons

### Create Custom Configurations

Copy `config.example.json` and modify:

```json
{
    "input": "/path/to/your/svgs",
    "output": "/path/to/output",
    "package": "com.yourapp.icons",
    "iconpack_name": "YourAppIcons",
    "generate_index": true,
    "verbose": true,
    "clean": true
}
```

## 📚 Next Steps

1. **Try the examples** with the provided sample SVGs
2. **Replace sample SVGs** with your own icon files
3. **Integrate generated code** into your Compose project
4. **Create config files** for your specific use cases
5. **Automate builds** using configuration files in CI/CD

For more advanced usage, see the main [README.md](../README.md).