# Lab 5 – Reflection

The handout PDF did not list the four reflection questions, so these are the standard ones for this lab.

**1. Which issues were the easiest and which were the hardest to fix?**
Flake8 issues were the easiest: they are mechanical (blank lines, line length) and `autopep8` fixes most of them. Docstrings and the f-string/naming warnings were also quick. The hardest was replacing `pickle`: JSON turns integer keys into strings, so `restore_orders` had to convert them back, and removing the `global` statements and the `order_history=[]` default meant rethinking how order ids are generated (`max(orders, default=0) + 1`).

**2. Did the tools report any false positives, or miss real problems?**
No outright false positives, but the severities are debatable: Bandit rated `import pickle` Low while the matching `pickle.load` was Medium, and for a local backup file the real-world risk is modest unless the file can be tampered with. More importantly, the tools missed logic bugs: unknown dishes billed at 99, invalid statuses like "teleported" accepted, empty orders accepted, and unknown order ids ignored. Those only showed up by running the program and reading its output.

**3. How could static analysis be integrated into a real development workflow?**
Run Flake8 and Pylint as pre-commit hooks so style and quality errors never reach the repo, and run all three tools in CI (for example GitHub Actions) on every pull request, failing the build on Bandit Medium/High findings or a Pylint score below a threshold such as 9.5. Keep configuration (`.pylintrc`, `setup.cfg`) in the repo so everyone uses the same rules, and use targeted suppressions (with a comment explaining why) instead of disabling checks globally.

**4. What tangible improvements did you see in code quality, security and maintainability?**
Pylint went from 6.27 to 10.00, Bandit from 3 findings to 0, and Flake8 from 12 to 0. Beyond the numbers: the code no longer depends on unsafe deserialization, errors are no longer swallowed silently, files are closed reliably, state changes are easier to follow without `global`, functions are documented, and bad input is rejected with a clear message. The code is also importable without running the demo, which makes it testable.
