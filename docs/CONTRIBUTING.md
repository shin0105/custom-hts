# Contributing to Custom HTS

Thank you for your interest in contributing to Custom HTS! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Follow the [Setup Guide](SETUP.md) to configure your development environment
4. Create a new branch for your feature or bug fix

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

or

```bash
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Follow the coding guidelines in `.github/instructions/`:
- Python code: Follow `.github/instructions/python.instructions.md`
- TypeScript code: Follow `.github/instructions/typescript.instructions.md`
- Security: Follow `.github/instructions/security.instructions.md`

### 3. Write Tests

- Add tests for new features
- Ensure all tests pass before submitting

Backend tests:
```bash
cd backend
uv run pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

### 4. Format Your Code

Backend:
```bash
cd backend
uv run black src tests
uv run flake8 src tests
```

Frontend:
```bash
cd frontend
npm run format
npm run lint
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "Add feature: description of what you added"
```

or

```bash
git commit -m "Fix: description of what you fixed"
```

### 6. Push and Create Pull Request

```bash
git push origin your-branch-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Reference to any related issues
- Screenshots for UI changes

## Areas for Contribution

### High Priority

1. **Testing**
   - Add more unit tests
   - Add integration tests
   - Add end-to-end tests

2. **Documentation**
   - Improve API documentation
   - Add more code examples
   - Create video tutorials

3. **Features**
   - Real-time data updates via WebSocket
   - Advanced charting capabilities
   - User authentication
   - Portfolio tracking

### Medium Priority

1. **Performance**
   - Optimize database queries
   - Implement better caching
   - Reduce bundle sizes

2. **UI/UX**
   - Mobile responsiveness
   - Dark mode
   - Accessibility improvements
   - Internationalization (i18n)

3. **DevOps**
   - Docker configuration
   - CI/CD pipelines
   - Deployment guides

### Low Priority

1. **Code Quality**
   - Refactoring
   - Code organization
   - Type safety improvements

## Coding Standards

### Python (Backend)

- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Maximum line length: 79 characters
- Use meaningful variable names

Example:
```python
def calculate_change_percent(
    current: float, previous: float
) -> Optional[float]:
    """
    Calculate percentage change between two values.

    Args:
        current: Current value
        previous: Previous value

    Returns:
        Percentage change or None if calculation not possible
    """
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100
```

### TypeScript (Frontend)

- Use strict mode
- Define explicit types
- Use functional components
- Follow React best practices
- Use meaningful component names

Example:
```typescript
interface StockCardProps {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
}

export const StockCard: React.FC<StockCardProps> = ({
  symbol,
  name,
  currentPrice,
  change,
}) => {
  return (
    <div className="stock-card">
      {/* Component content */}
    </div>
  );
};
```

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted
- [ ] Documentation is updated
- [ ] No console.log or debug statements
- [ ] API keys are not committed

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test the changes

## Screenshots
If applicable, add screenshots

## Checklist
- [ ] Tests pass
- [ ] Code is formatted
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Reporting Issues

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, browser, Python/Node version)
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case and benefits
- Proposed implementation (if any)
- Mockups or examples (if applicable)

## Questions?

- Check existing issues and pull requests
- Read the documentation
- Ask in GitHub Discussions
- Open an issue for clarification

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Custom HTS! 🎉
