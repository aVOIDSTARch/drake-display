# Setting Up the `fields` Project — src layout + pyproject.toml

This walks you through modern Python packaging as of 3.14. The old way was a `setup.py` script that *executed code* to describe your package. The new way is `pyproject.toml` — a static, declarative config file, no code execution required to know what your package is. That's the whole philosophical shift: **description, not imperative script.**

---

## Step 1 — Directory skeleton

Why `src/` and not just dropping `.py` files in the project root? Because without it, Python can accidentally import your *uninstalled, working-directory* code instead of the properly installed package — masking bugs that only show up after you actually ship it. The `src/` layout forces every import to go through a real install step, so what you test is what you'll actually distribute.

```bash
mkdir -p fields-project/src/fields
mkdir -p fields-project/tests
cd fields-project
```

Result:

```text
fields-project/
├── src/
│   └── fields/
│       └── __init__.py
├── tests/
└── pyproject.toml
```

`__init__.py` marks `fields/` as an importable package. Create it empty for now:

```bash
touch src/fields/__init__.py
```

---

## Step 2 — `pyproject.toml`

This single file replaces `setup.py`, `setup.cfg`, and `requirements.txt`'s job of declaring metadata. Create `pyproject.toml` in the project root:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "fields"
version = "0.1.0"
description = "Composable scalar field library for weighted spatial influence."
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.26",
]

[tool.hatch.build.targets.wheel]
packages = ["src/fields"]
```

**What each part means, since you're new to the format:**

- `[build-system]` tells Python's tooling *what program builds this package*. We're using **hatchling** — a modern, lightweight build backend. (The older default was `setuptools`; hatchling is simpler for pure-Python projects like ours and has cleaner `src/`-layout support out of the box.)
- `[project]` is the **PEP 621** standard table — this is the "evolving toml concept" you noticed. It's a spec, not a hatchling-specific thing, meaning any compliant tool (pip, hatch, poetry, uv) reads this identically.
- `dependencies` replaces `requirements.txt` for your actual library dependencies. We need `numpy` for the vectorized field math.
- `[tool.hatch.build.targets.wheel]` tells hatchling explicitly where the real source lives, since we're not using the flat layout it might otherwise guess at.

---

## Step 3 — Virtual environment

Never install project dependencies into your system Python — a venv isolates this project's packages from everything else on your machine.

```bash
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
```

Your shell prompt should now show `(.venv)`. Everything you `pip install` from here goes into this isolated folder, not system-wide.

---

## Step 4 — Editable install

```bash
pip install -e .
```

The `-e` flag means **editable** — pip links to your `src/fields` directory rather than copying it, so changes to your `.py` files are immediately visible to anything that does `import fields`, with no reinstall step. This is what makes iterative development sane.

Verify it worked:

```bash
python3 -c "import fields; print(fields.__file__)"
```

It should print a path pointing into `src/fields/__init__.py`.

---

## Step 5 — Add pytest (for later, when we write tests)

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0"]
```

Add this table to `pyproject.toml`, then:

```bash
pip install -e ".[dev]"
```

The `.[dev]` syntax installs the base package **plus** the optional `dev` dependency group — this is how you separate "what a user of your library needs" from "what a contributor developing it needs."

---

## Checkpoint

Run this to confirm everything is wired correctly:

```bash
python3 -c "import fields, numpy; print('OK:', fields.__name__, numpy.__version__)"
```

If that prints without error, the project skeleton is live. Next step will be dropping the `Kernel` ABC into `src/fields/kernels.py`.

**Question for you before we proceed:** do you want `tests/` to mirror `src/fields/`'s internal structure 1:1 (e.g., `tests/test_kernels.py` ↔ `src/fields/kernels.py`) as we add modules, or would you rather I explain that convention when we get there?
