"""
_naming.py

Single source of fallback names for unnamed factors, shared by
SourceField and config validation so the two can never hand out
the same "unnamed_factor_N" twice.
"""

import itertools

_unnamed_counter = itertools.count()


def generate_unnamed_fallback() -> str:
    return f"unnamed_factor_{next(_unnamed_counter)}"
