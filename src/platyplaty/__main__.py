#!/usr/bin/env python3
"""Entry point for python -m platyplaty."""

from platyplaty.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1) from None
