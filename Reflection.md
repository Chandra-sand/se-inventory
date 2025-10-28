# Lab 5 Reflection

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

* **Easiest:** 
style/formatting and obvious risks. Removing the unused logging import, adding required blank lines/newline at EOF, converting old-style string formatting to f-strings, and deleting eval were quick, mechanical changes with zero ambiguity

* **Hardest:** 
correctness and robustness changes. Replacing the bare except with explicit logic, adding strict input validation for item and qty, fixing the mutable default argument pattern, and making file I/O safe with context managers, encoding, and atomic writes required design decisions and light refactoring to avoid side effects on behavior.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Mostly accurate, but a borderline case: after removing eval, tools may still flag references if left in comments or tests; this can look like a “false positive” in context even though the rule is correct in general. Similarly, some style suggestions (e.g., naming or “consider using with”) can be contextually acceptable but still flagged; these are not strictly false, just opinionated. One concrete example encountered: import logging flagged as unused even though it was intended for future log wiring; the warning is correct, but the developer intent made it feel like a false positive before logging was actually used

### 3. How would you integrate static analysis tools into your actual software development workflow?

Local dev: enable linting and code actions in the editor; add a pre-commit hook to run formatters and linters (e.g., ruff/flake8, pylint, bandit) so obvious issues never reach commits. Keep strict rules for security and correctness, relaxed rules for style initially, and tighten over time.​

CI gates: run lint/security jobs on every push and pull request. Fail the build on high/medium severity security findings and bare except patterns; surface style/doc issues as warnings or separate non-blocking jobs early on, then promote to blocking once the codebase is clean. Upload annotated reports to PRs for fast feedback.​

Configuration: check in shared configs (pyproject.toml or tool-specific files) to ensure consistent rules across machines; document common suppressions and require justification for any ignore pragmas in code review

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

Code quality and readability: consistent snake_case names, docstrings, and spacing made functions easier to scan and understand; f-strings improved clarity; removing dead imports reduced noise.​

Robustness and safety: eliminating eval, removing bare except, validating inputs, and using context managers with explicit UTF-8 encoding reduced security and runtime risks; atomic saves lowered the chance of corrupt files.​

Maintainability: avoiding mutable default args, not rebinding globals (clearing/updating instead), and adding small helper validators made behavior more predictable and testable over time.


