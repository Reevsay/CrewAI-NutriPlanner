# Contributing to CrewAI-NutriPlanner

Thank you for your interest in contributing to CrewAI-NutriPlanner! This document provides guidelines for contributing to this multi-agent AI meal planning system.

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/CrewAI-NutriPlanner.git
   cd CrewAI-NutriPlanner
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure APIs**
   ```bash
   cp .env.example .env
   # Add your Google Gemini API key to .env
   ```

4. **Validate Setup**
   ```bash
   python scripts/validate_setup.py
   ```

## 🎯 How to Contribute

### Types of Contributions Welcome

- **🐛 Bug Reports**: Help identify and fix issues
- **✨ Feature Requests**: Suggest new AI agents or capabilities
- **📝 Documentation**: Improve guides, examples, and API docs
- **🔧 Code Contributions**: Implement features, optimize performance
- **🧪 Testing**: Add test coverage, improve test quality
- **🤖 AI Improvements**: Enhance agent coordination and intelligence

### Development Guidelines

#### Code Style
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

#### Commit Messages
Use conventional commit format:
```
feat(agents): add recipe optimization algorithm
fix(api): handle nutrition API timeout errors
docs(readme): update installation instructions
test(integration): add end-to-end workflow tests
```

#### Branch Naming
```
feature/agent-optimization
bugfix/api-timeout-handling
docs/user-guide-improvements
test/integration-coverage
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Test specific components
pytest tests/test_agents/
pytest tests/test_integration/
```

### Writing Tests
- **Unit Tests**: Test individual agent functions
- **Integration Tests**: Test agent communication
- **End-to-End Tests**: Test complete workflows

## 🏗️ Architecture Guidelines

### Adding New AI Agents
1. Inherit from `BaseAgent`
2. Follow single responsibility principle
3. Use structured data models (Pydantic)
4. Implement proper error handling
5. Add comprehensive tests

### Tool Development
1. Inherit from `BaseTool`
2. Handle errors gracefully
3. Implement caching where appropriate
4. Document API requirements

## 📝 Documentation

### Code Documentation
- Use Google-style docstrings
- Include type hints
- Document complex algorithms
- Provide usage examples

### User Documentation
- Update README for new features
- Add examples to User Guide
- Document API changes
- Include troubleshooting tips

## 🔄 Pull Request Process

### Before Submitting
1. **Run Tests**: `pytest`
2. **Check Code Quality**: `black`, `flake8`, `mypy`
3. **Update Documentation**: Add/update relevant docs
4. **Test Manually**: Verify changes work end-to-end

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] Documentation files updated
- [ ] Examples added/updated
```

## 🐛 Bug Reports

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected vs Actual Behavior
- Expected: What should happen
- Actual: What actually happens

## Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- CrewAI Version: [e.g., 0.1.0]

## Additional Context
- Error messages
- Log files
- Screenshots
```

## ✨ Feature Requests

### Feature Request Template
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## AI Agent Impact
Which agents would be affected? How would they coordinate?

## Implementation Ideas
Technical approach suggestions (optional)
```

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the technical merits

### Communication
- **GitHub Issues**: Bug reports and feature requests
- **Pull Request Comments**: Code-specific discussions
- **Discussions**: General questions and ideas

## 🏆 Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Major contributions highlighted
- **README**: Special thanks section

## 📚 Resources

### Learning Resources
- [CrewAI Documentation](https://docs.crewai.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)

### Development Tools
- **IDE**: VS Code with Python extension recommended
- **Debugging**: Built-in debugger or pdb
- **API Testing**: Postman or curl for API testing

Thank you for contributing to CrewAI-NutriPlanner! 🎉