# Agent Guidelines & Project Setup

Welcome to the `CommuCraft-AI` project! All agents and contributors must adhere to the following setup and coding guidelines.

## 1. Package Management with `uv`

This project uses `uv` as the default Python package manager and resolver.

- **Adding dependencies:** Use `uv add <package_name>` to add a standard dependency.
- **Adding dev dependencies:** Use `uv add --dev <package_name>` for development tools (like pytest or ruff).
- **Syncing environment:** Use `uv sync` to ensure your local virtual environment is up to date with `pyproject.toml` and `uv.lock`.
- **Running commands:** Always run scripts or tools within the `uv` environment using `uv run <command>` (e.g., `uv run python -m commucraft_ai.main` or `uv run pytest`).

## 2. Testing Setup

We use `pytest` for executing minimal tests.

- **Setup:** If not already installed, add pytest by running `uv add --dev pytest`.
- **Structure:** Place all test files inside a `tests/` directory at the project root.
- **Naming Convention:** Test files must be named starting with `test_*.py`, and test functions must start with `test_`.
- **Execution:** Run tests using `uv run pytest`.

**Example minimal test (`tests/test_main.py`):**

```python
def test_basic_addition() -> None:
    assert 1 + 1 == 2
```

## 3. Coding Style & Linting

We strictly enforce coding standards using `ruff`.

- **Linter & Formatter:** Use `ruff` to manage formatting, PEP8 compliance, and import sorting.
  - Check code: `uv run ruff check .`
  - Format code: `uv run ruff format .`
  - Fix auto-fixable issues (like import sorting): `uv run ruff check --fix .`
- **Line Length Limit:** We use a **120-character** line limit instead of the traditional 80 characters.
  *(Note: This should be reflected in the `pyproject.toml` configuration under `[tool.ruff]` with `line-length = 120`)*.
- **Type Hints:** **ALWAYS** use complete type hints in all function definitions for both arguments and return types.
- **Docstrings:** All functions must include descriptive docstrings detailing what the function does, an `Args` section, a `Returns` section, and an `Errors` section if applicable.
- **Agent Tools:** When writing tools for the agent, the docstring must also include an `Example` section demonstrating `Input` and `Output`.

**Example of expected function style:**

```python
def format_greeting(name: str, greeting_prefix: str = "Hello", repeat_count: int = 1) -> list[str]:
    """
    Returns a list of formatted greeting strings.

    Args:
        name (str): The name of the person to greet.
        greeting_prefix (str, optional): The prefix of the greeting. Defaults to "Hello".
        repeat_count (int, optional): The number of times to repeat the greeting. Defaults to 1.

    Returns:
        list[str]: A list containing the formatted greeting strings.

    Errors:
        ValueError: If repeat_count is less than 0.

    Example:
        Input: format_greeting("Alice", "Hi", 2)
        Output: ["Hi, Alice!", "Hi, Alice!"]
    """
    if repeat_count < 0:
        raise ValueError("repeat_count must be non-negative")
    return [f"{greeting_prefix}, {name}!"] * repeat_count
```

## 4. Code Quality Standards

### Type Safety
- All functions must have complete type annotations for parameters and return values.
- Use modern Python typing constructs (e.g., `list[str]` instead of `List[str]`).
- Avoid using `Any` type unless absolutely necessary; be explicit about types.

### Documentation
- Every function, class, and module should have clear docstrings following the NumPy/Google style format.
- Include practical examples in docstrings for public APIs and tools.
- Keep comments minimal; write self-documenting code with clear variable and function names.

### Error Handling
- Define custom exceptions when appropriate for domain-specific errors.
- Include the `Errors` section in docstrings to document possible exceptions.
- Handle errors gracefully and provide meaningful error messages.

## 5. Development Workflow

### Before Committing
1. Run `uv run ruff check --fix .` to auto-fix linting issues.
2. Run `uv run ruff format .` to ensure consistent formatting.
3. Run `uv run pytest` to ensure all tests pass.
4. Verify that your code follows all guidelines outlined in this document.

### Git Workflow
- Create feature branches with descriptive names (e.g., `feature/add-user-auth`).
- Write clear, concise commit messages.
- Ensure all tests pass before pushing to remote.

## 6. Project Structure

```
CommuCraft-AI/
├── src/
│   └── commucraft_ai/
│       ├── __init__.py
│       ├── main.py
│       └── [module_files]
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── pyproject.toml
├── uv.lock
├── AGENTS.md (this file)
└── README.md
```

## 7. Dependencies & Environment

- **Python Version:** Specify the minimum Python version in `pyproject.toml` (typically 3.9+).
- **Dependency Updates:** Always use `uv sync` after modifying `pyproject.toml` to update your local environment.
- **Lock File:** The `uv.lock` file should be committed to version control to ensure reproducible builds.

## 8. Continuous Integration

- All code must pass `ruff check` and `ruff format` checks.
- All tests must pass with `uv run pytest`.
- Pull requests should include descriptions of changes and any relevant issue numbers.

---

**Last Updated:** March 23, 2026

For more information or to report issues with these guidelines, please open an issue in the project repository.
