"""Entry point for CommuCraft-AI (deprecated - use 'commucraft-ai' CLI instead).

This module serves as a backwards-compatible entry point for the application.
It delegates to the actual implementation in src/commucraft_ai/main.py.

PREFERRED USAGE (via CLI entry point from pyproject.toml):
    commucraft-ai                   # Run scheduler for configured time
    commucraft-ai --now             # Run immediately and exit (for testing)
    uv run commucraft-ai            # Same, with uv package manager

LEGACY USAGE (still works but deprecated):
    python main.py                  # Run scheduler
    python main.py --now            # Run immediately
    python -m commucraft_ai.main    # Direct module execution (requires src in path)

The new CLI command is the recommended way to run CommuCraft-AI.
"""

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add src directory to Python path so imports work correctly
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    from commucraft_ai.main import main

    # Pass command-line arguments to main function
    main(sys.argv[1:])
