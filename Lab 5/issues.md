# Static analysis findings

The line numbers below refer to the original `blood_donation.py` before fixes.
Severity labels are from the actual Bandit output where applicable; the other
rows describe Pylint/Flake8 findings or a functional issue found during review.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command uses untrusted input | Security — Bandit B605, High | 65 | `os.system` builds a shell command from phone numbers, allowing shell metacharacters to change the command. | Use `subprocess.run` with an argument list and `check=True`, so no shell parses the values. |
| Unsafe temporary file creation | Security — Bandit B306, Medium | 60 | `tempfile.mktemp` returns a name without creating/reserving the file, leaving a race window. | Use `tempfile.mkstemp`, close its descriptor, then return the reserved path. |
| Mutable default argument | Correctness — Pylint W0102 | 17 | The default `notes=[]` is shared across calls; rejected donor notes could leak between registrations. | Default to `None` and only append when a notes list is explicitly supplied. |
| Broad exception handling | Robustness — Pylint W0718 | 42–46 | `except Exception` hides unrelated programming errors in addition to an unknown patient blood group. | Use an explicit compatibility lookup and return zero only when the requested group is unknown. |
| Assertion used for input validation | Security/robustness — Bandit B101 | 18 | Python can remove assertions under optimization, so the blood group validation is not reliable. | Raise `ValueError` explicitly for an unknown donor blood group. |
| Hardcoded officer password | Security — Bandit B105, Low | 5 | An unused password literal is embedded in source and could be mistaken for a real credential. | Remove the unused constant; no password is needed by this demo. |
| Compatibility missing for four patient groups | Functional correctness | 11–16 | The original map omitted A-, B-, AB-, and B- patient compatibility, causing valid queries to be treated like unknown groups. | Add compatible donor group lists for every supported blood group. |
| Non-PEP 8 names and missing docstrings | Maintainability — Pylint | 17–81 | Public functions/parameters use camelCase and functions/module lack docstrings, obscuring the interface and lowering the score. | Rename to snake_case and document module and functions. |
| Style violations | Style — Flake8 E501/E303/E261/E225 | 7, 58, 80, 81 | Overlong line, excess blank lines, insufficient inline-comment spacing, and missing assignment spacing. | Wrap the mapping, remove extra blank lines, and apply standard spacing. |
