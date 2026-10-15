# Lab 5 – Issues Found and Fixed (`delivery_system.py`)

Line numbers refer to the original file. Tool results: Pylint 6.27 → 10.00/10, Bandit 3 issues (1 Medium, 2 Low) → 0, Flake8 12 → 0.
Reports are in `reports/before/` and `reports/after/`.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Unsafe deserialization with `pickle.load` (B301, CWE-502) | Security (Bandit, Medium) | 49 | Loading a pickle file can execute arbitrary code if `orders.pkl` is tampered with. | Replaced pickle with JSON (`orders.json`); convert string keys back to `int` on restore. Commit 1. |
| `import pickle` (B403) | Security (Bandit, Low) | 2 | Importing pickle flags the risk above. | Removed the import together with the pickle usage. |
| `try / except / pass` swallows errors (B110, E722, W0702) | Security + Bug | 22-25 | Bare `except` hides unknown order ids and every other error, so the caller never learns the update failed. | Catch only `KeyError` and re-raise with a clear message; callers in `main` handle it and print it. |
| Invalid status accepted | Bug (not flagged by tools) | 21-25 | `"teleported"` was stored as a status, so the queue held values outside `VALID_STATUSES` (the list was never used). | Validate against `VALID_STATUSES` and raise `ValueError`. |
| Mutable default argument `order_history=[]` (W0102) | Bug (Pylint) | 11, 17, 19 | The list is shared across calls; it also made the returned id depend on hidden state. | Removed the parameter; the new id comes from `max(orders, default=0) + 1`, which also stays correct after a restore. |
| Unknown dishes silently cost 99 | Bug (not flagged by tools) | 15 | `sushi` was billed at 99, giving wrong totals (Ravi's order showed 249). | Raise `ValueError("Not on the menu: ...")`; total is `sum(menu[i] ...)`. |
| Empty customer / empty order accepted | Bug (not flagged by tools) | 16, 60 | Order #3 had no customer, no items and total 0, and was later marked delivered. | Validate customer name and at least one item in `create_order`. |
| `global` statements (W0603) | Design (Pylint) | 12, 28, 48 | Rebinding module globals makes state hard to follow and test. | Mutate the shared dicts in place (`clear`/`update`); no `global` needed. |
| Invalid constant name `next_id` (C0103) | Style (Pylint) | 7 | Module-level counter did not follow naming rules. | Removed the variable entirely (id is derived from `orders`). |
| Broad `except Exception` (W0718) | Quality (Pylint) | 32 | Hides programming errors while reading the menu. | Catch `OSError` and `json.JSONDecodeError` only; fall back to `DEFAULT_MENU`. |
| Files opened without `with` / encoding (R1732, W1514) | Resource leak (Pylint) | 30, 43, 49 | File handles leak if an exception occurs; encoding depends on the platform. | Use `with open(..., encoding="utf-8")`. |
| Missing module/function docstrings (C0114, C0116) | Documentation (Pylint) | 1, 11, 21, 27, 35, 42, 47, 51, 56 | No description of purpose or error behaviour. | Added docstrings. |
| `printQueue` not snake_case (C0103) and `%` formatting (C0209) | Style (Pylint) | 51-52 | Naming and string formatting out of line with PEP 8 conventions. | Renamed to `print_queue`; used an f-string. |
| `main()` runs on import | Design (not flagged) | 70 | Importing the module runs the whole demo. | Added `if __name__ == "__main__":` guard. |
| E302 / E305 blank lines | Style (Flake8) | 11, 21, 27, 35, 42, 47, 51, 56, 70 | Two blank lines required around top-level definitions. | Fixed formatting (Commit 3). |
| E501 line too long | Style (Flake8) | 16, 54 | Lines exceeded 79 characters. | Wrapped long lines. Commit 3. |

## Commits
1. `fix(bandit)`: pickle → JSON, remove silent try/except/pass
2. `fix(pylint)`: docstrings, no globals/mutable default/broad except, naming, validation
3. `style(flake8)`: PEP 8 blank lines and line length

## Behaviour change to be aware of
The demo in `main()` now *rejects* the bad inputs (sushi, empty order, "teleported", order 42) and prints why, instead of accepting them. Output: revenue 290, queue shows only Asha's delivered order.
