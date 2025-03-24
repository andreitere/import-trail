# 🕸️ Import Trail

Ever wondered *how exactly* your Python files are wired together?  
This little tool helps you trace the full chain of imports in your project — from your entry file all the way down the rabbit hole.

## 🔍 What It Does

This CLI tool recursively scans your Python project and prints out full import chains, showing you exactly how and where each file or module gets pulled in.

It supports:
- Regular imports (import foo.bar)
- Relative imports (from . import something)
- Deep/nested imports (from foo.bar.baz import x)
- Dynamic imports (importlib.import_module(), __import__())

## 💡 Why?

Because sometimes you just want to know why a file is even being imported — and grep won't cut it.

## ⚙️ Usage

    python -m import_trail <entry_file> [project_root]

Or, if you’ve installed it:

    import-trail <entry_file> [project_root]

Arguments:
- <entry_file> — the starting point (e.g., main.py)
- [project_root] — optional; defaults to the folder containing the entry file

## 📌 Example

    import-trail src/main.py src/

Output looks like:

    main -> utils.logger
    main -> services.db -> models.user -> utils.helpers

Each line shows the complete import path from your entry file to a specific module.

## 🛠 Structure

    import-trail/
    ├── import_trail/
    │   ├── __main__.py
    │   └── core.py
    ├── pyproject.toml
    └── README.md

## 📎 Notes & Quirks

- Only tracks files/modules within your project root
- Ignores standard library and external packages
- Dynamic imports must use string literals to be detected
- May miss edge cases — it's not a static analyzer powerhouse

## ⚠️ Disclaimer

This is pretty untested, probably has edge cases, and might break in weird scenarios…  
But hey — it’s already handy. Enjoy! :)

## 📄 License

MIT. Hack freely.
