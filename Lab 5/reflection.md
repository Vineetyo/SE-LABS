# Reflection

The README refers to a lab handout, but no handout or reflection questions were
present in the provided workspace. These are four drafted answers to relevant
reflection questions; they are not quoted from the handout.

1. **What did the analysis tools reveal?** Bandit found a high severity shell
   invocation built from donor phone numbers and a medium severity temporary
   file race. It also reported a hardcoded password and an assertion used for
   validation. Pylint identified a shared mutable default and broad exception
   handling, alongside naming and documentation problems. Flake8 found four
   formatting violations.

2. **Which issue was most important, and why?** The shell command was the most
   serious because phone numbers are input values and shell parsing can turn
   special characters into unintended commands. Passing an argument list to
   `subprocess.run` prevents shell interpretation and `check=True` reports
   execution failures.

3. **How did the fixes preserve or improve behavior?** The demo still registers
   eligible donors, applies the 90-day gap, updates stock, and prints the same
   outputs. Unknown patient groups still yield zero units. Every supported
   blood group now has a compatibility entry, while invalid donor groups raise
   an explicit `ValueError` instead of depending on an assertion.

4. **What will you take from this lab?** Static analyzers highlight risks and
   maintainability problems, but their output needs review in context. I
   prioritized the actual security and correctness findings, fixed each at
   its source, and reran the tools to check that changes addressed the reported
   issues without hiding warnings.
