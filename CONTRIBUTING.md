# Contributing to Job-Genie

We love your input! We want to make contributing to Job-Genie as easy and transparent as possible.

## Development Process

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Setting Up Development Environment

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Installation

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR-USERNAME/Job-Genie.git
cd Job-Genie
```

2. Create a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements-updated.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

6. Download spaCy models:
```bash
python -m spacy download en_core_web_sm
```

## Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
black .
isort .
flake8 scripts/
mypy scripts/
```

## Testing

We use pytest for testing. Run tests with:

```bash
pytest tests/ -v --cov=scripts
```

### Writing Tests

- Place test files in the `tests/` directory
- Name test files with `test_` prefix
- Write descriptive test names
- Use fixtures for common test data
- Mock external dependencies

Example test:
```python
def test_security_validator_sanitizes_filename():
    dangerous_name = "file<script>.pdf"
    result = SecurityValidator.sanitize_filename(dangerous_name)
    assert "<script>" not in result
```

## Security Guidelines

- Never commit API keys or sensitive data
- Use the SecurityValidator for file operations
- Sanitize all user inputs
- Follow OWASP security guidelines
- Report security issues privately to maintainers

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update version numbers following [Semantic Versioning](https://semver.org/)
3. Ensure all tests pass and coverage is maintained
4. Get approval from at least one maintainer

## Reporting Bugs

Use GitHub Issues to track bugs. Include:

- Operating system and version
- Python version
- Full error message and stack trace
- Steps to reproduce
- Expected vs actual behavior

## Feature Requests

Open a GitHub Issue with:

- Clear description of the feature
- Use case and motivation
- Proposed implementation approach (if any)

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
