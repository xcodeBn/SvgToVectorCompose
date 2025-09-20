# Contributing to SvgToVectorCompose

Thank you for your interest in contributing to SvgToVectorCompose! We welcome contributions from the community and are grateful for any help you can provide.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Guidelines](#code-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Getting Started

Before you begin contributing, please:

1. Read this contributing guide thoroughly
2. Check the [existing issues](https://github.com/xcodebn/SvgToVectorCompose/issues) to see if your idea or bug report already exists
3. Fork the repository and clone it locally
4. Set up your development environment

## Development Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SvgToVectorCompose.git
   cd SvgToVectorCompose
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the installation:**
   ```bash
   python main.py --help
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes** - Fix issues with SVG parsing, Kotlin generation, or CLI functionality
- **Feature enhancements** - Add new SVG element support, improve IconPack generation, etc.
- **Documentation** - Improve README, add examples, create tutorials
- **Performance improvements** - Optimize conversion speed, memory usage
- **Code quality** - Refactor code, add type hints, improve error handling

### Before You Start

- **For bug fixes**: Create an issue describing the bug unless one already exists
- **For new features**: Open an issue to discuss the feature before implementing
- **For documentation**: Small improvements can be made directly; for major changes, please discuss first

## Code Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where possible
- Write descriptive variable and function names
- Add docstrings for classes and functions
- Keep functions focused and small

### Example Code Style

```python
def parse_svg_element(element: ET.Element, parent_transform: str = "") -> Optional[PathData]:
    """
    Parse an SVG element and convert it to PathData.
    
    Args:
        element: The XML element to parse
        parent_transform: Transform from parent elements
        
    Returns:
        PathData object or None if parsing fails
    """
    if element.tag.endswith('path'):
        return self._parse_path_element(element, parent_transform)
    elif element.tag.endswith('polygon'):
        return self._parse_polygon_element(element, parent_transform)
    return None
```

### Kotlin Code Generation

- Generated Kotlin code should follow Kotlin conventions
- Use PascalCase for ImageVector names
- Ensure proper package structure
- Maintain consistent formatting

## Testing

### Manual Testing

Since we don't have automated tests yet, please test your changes manually:

1. **Test with simple SVGs:**
   ```bash
   python main.py -i test_icons -o test_output -p com.test.icons --generate-index
   ```

2. **Test with complex SVGs (if available):**
   - Test with IntelliJ icons or Material Design icons
   - Verify conversion success rate

3. **Test CLI functionality:**
   - Test all command-line options
   - Test interactive mode
   - Test configuration file loading

4. **Test edge cases:**
   - Empty directories
   - Invalid SVG files
   - Special characters in filenames
   - Nested directory structures

### Adding Tests

We welcome contributions that add proper testing infrastructure:

- Unit tests for individual components
- Integration tests for full conversion process
- Test fixtures with known SVG files
- Automated testing setup

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the code guidelines
   - Test thoroughly
   - Update documentation if needed

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```

4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request:**
   - Use a clear, descriptive title
   - Describe what your PR does and why
   - Reference any related issues
   - Include screenshots if applicable

### Pull Request Template

When creating a PR, please include:

```markdown
## Description
Brief description of what this PR does.

## Changes Made
- List of specific changes made
- New features added
- Bugs fixed

## Testing
- [ ] Tested with simple SVG files
- [ ] Tested with complex SVG files
- [ ] Tested CLI functionality
- [ ] Tested edge cases

## Related Issues
Fixes #issue_number (if applicable)
```

## Reporting Issues

When reporting bugs, please include:

1. **Environment information:**
   - Python version
   - Operating system
   - Command used

2. **Problem description:**
   - What you expected to happen
   - What actually happened
   - Steps to reproduce

3. **Sample files (if possible):**
   - SVG file that causes the issue
   - Generated output (if any)
   - Error messages

### Issue Template

```markdown
**Environment:**
- Python version: 
- OS: 
- Command: 

**Problem:**
Describe the issue...

**Expected behavior:**
What you expected to happen...

**Actual behavior:**
What actually happened...

**Additional context:**
Any other relevant information...
```

## Feature Requests

We welcome feature requests! When suggesting new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** - why would this feature be useful?
3. **Provide examples** - how would you use this feature?
4. **Consider implementation** - do you have ideas about how it could work?

### Popular Feature Ideas

- SVG animation support
- Additional export formats (Android XML, Flutter)
- GUI interface
- Web-based converter
- Plugin system for custom SVG elements
- Batch optimization tools

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume positive intent

## Getting Help

If you need help with contributing:

- Open a discussion on GitHub
- Comment on existing issues
- Reach out to maintainers

## Recognition

Contributors will be:

- Listed in the README
- Mentioned in release notes
- Appreciated in the community

Thank you for contributing to SvgToVectorCompose! 🎉