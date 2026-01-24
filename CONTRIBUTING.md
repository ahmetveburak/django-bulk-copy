# Contributing Guidelines

## Before Contributing

Welcome to [django-bulk-copy](https://github.com/ahmetveburak/django-bulk-copy)! Before sending your pull requests, make sure that you **read the whole guidelines**. If you have any doubt on the contributing guide, please feel free to [state it clearly in an issue](https://github.com/ahmetveburak/django-bulk-copy/issues/new).

## Contributing

### Contributor

We are very happy that you are considering contributing to this project! Being one of our contributors, you agree and confirm that:

- You did your work - no plagiarism allowed
  - Any plagiarized work will not be merged.
- Your work will be distributed under [MIT License](LICENSE.md) once your pull request is merged
- Your submitted work fulfills or mostly fulfills our styles and standards

**New implementations** are welcome! For example, new database backends, additional field type support, or performance improvements.

**Improving documentation** and **writing proper tests** are also highly welcome.

### Contribution

We appreciate any contribution, from fixing a grammar mistake in a comment to implementing new features. Please read this section if you are contributing your work.

Your contribution will be tested by our [automated testing on GitHub Actions](https://github.com/ahmetveburak/django-bulk-copy/actions). After you have submitted your pull request, you should see the GitHub Actions tests start to run at the bottom of your submission page. If those tests fail, click on the **details** button and try to read through the GitHub Actions output to understand the failure.

Please help us keep our issue list small by adding `fixes: #$ISSUE_NO` to the commit message of pull requests that resolve open issues. GitHub will use this tag to auto-close the issue when the PR is merged.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL (for running tests)
- uv (for dependency management)

### Setup

```bash
# Clone the repository
git clone https://github.com/ahmetveburak/django-bulk-copy.git
cd django-bulk-copy

# Install dependencies with uv
uv sync --all-extras

# Or use pip
pip install -e ".[postgres-binary]"

# Start PostgreSQL (using Docker)
docker run -d --name bulk_copy \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 postgres

# Run migrations
DJANGO_SETTINGS_MODULE=tests.settings python manage.py migrate

# Run tests
pytest tests/ --cov=bulk_copy
```

### Pre-commit Hooks

Use [pre-commit](https://pre-commit.com/#installation) to automatically format and check your code:

```bash
pip install pre-commit  # only required the first time
pre-commit install
```

The plugin will run every time you commit changes. You can also run it manually:

```bash
pre-commit run --all-files --show-diff-on-failure
```

## Coding Standards

### Python Version

We support Python 3.10 and higher. Use modern Python features like:
- Type hints with the `|` union syntax (e.g., `int | None`)
- f-strings for string formatting
- Walrus operator (`:=`) where appropriate

### Code Formatting

We use **Ruff** for linting and formatting. Run it before submitting:

```bash
# Check for issues
ruff check bulk_copy tests

# Auto-fix issues
ruff check --fix bulk_copy tests
```

### Type Checking

We use **mypy** for static type checking:

```bash
mypy bulk_copy
```

All public functions should have type hints:

```python
def bulk_copy(self, objs: Sequence[models.Model], batch_size: int | None = None) -> None:
    ...
```

### Security

We use **Bandit** to scan for security issues:

```bash
bandit -c pyproject.toml -r bulk_copy
```

**Important security guidelines:**
- Always use `connection.ops.quote_name()` for SQL identifiers
- Always use parameterized queries for values
- Never use f-strings with user input in SQL queries

### Testing

Write tests for all new functionality:

```bash
# Run all tests with coverage
pytest tests/ --cov=bulk_copy --cov-report=term-missing

# Run specific test file
pytest tests/bulk_test/tests/test_manager.py

# Run with verbose output
pytest tests/ -v
```

Test files should be placed in `tests/bulk_test/tests/` and named `test_*.py`.

### Naming Conventions

Follow [PEP 8](https://pep8.org/#prescriptive-naming-conventions):
- `variable_names` and `function_names` should be `lower_case`
- `CONSTANTS` should be `UPPERCASE`
- `ClassNames` should be `CamelCase`

Use descriptive names:
```python
# Good
def get_sequence_generator() -> Generator:
    ...

# Avoid
def get_seq() -> Generator:
    ...
```

### Documentation

- Add docstrings to public methods
- Include type information in docstrings if complex
- Document any side effects or important caveats

```python
def bulk_copy(self, objs: Sequence[models.Model], batch_size: int | None = None) -> None:
    """
    Insert objects using PostgreSQL COPY command for better performance.

    Args:
        objs: Sequence of model instances to insert.
        batch_size: Optional batch size for processing large datasets.

    Note:
        Django signals (pre_save, post_save) are NOT fired.
    """
```

## Pull Request Process

1. Fork the repository and create a feature branch
2. Make your changes with appropriate tests
3. Ensure all tests pass: `pytest tests/`
4. Ensure code quality checks pass:
   - `ruff check bulk_copy tests`
   - `mypy bulk_copy`
   - `bandit -c pyproject.toml -r bulk_copy`
5. Submit a pull request with a clear description of changes

## Questions?

Feel free to open an issue if you have questions about contributing.

---

Writer [@onuralpszr](https://github.com/onuralpszr), Dec 2023.
Updated Jan 2026.
