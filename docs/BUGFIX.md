# Debugging story: reproduce → diagnose → fix

This documents a real bug-and-fix cycle in this project, to demonstrate the
JD requirement: *"identify, reproduce, and help resolve software issues."*

**Do this yourself before the interview** so the story is genuinely yours —
the steps are below. It takes ~15 minutes.

---

## The exercise

### 1. Introduce a bug
In `app/validators.py`, change the voltage ceiling so it's wrong:

```python
# BEFORE (correct)
VOLTAGE_MAX = 1000.0

# AFTER (bug introduced)
VOLTAGE_MAX = 100.0
```

### 2. Reproduce it — run the tests
```bash
pytest tests/unit -v
```

You'll see a failure like:

```
test_voltage_validation[400.0-True] FAILED
    assert is_voltage_valid(400.0) is True
    AssertionError: assert False is True
```

**This is "reproducing" the bug** — you've made it fail reliably and on demand.
A vague report ("readings are getting rejected") is now a specific, repeatable
failure with an exact assertion.

### 3. Diagnose it
The test tells you exactly what's wrong: a normal 400V reading is being marked
invalid. Trace it back — `is_voltage_valid(400)` returns `False` because the
ceiling is now 100. The validation logic is rejecting good data.

### 4. Fix it
Restore the correct ceiling:

```python
VOLTAGE_MAX = 1000.0
```

Re-run:
```bash
pytest tests/unit -v   # all green again
```

### 5. Commit both steps (shows the workflow)
```bash
git commit -am "Introduce voltage ceiling bug for debugging demo"
git commit -am "Fix: restore correct 1000V voltage ceiling"
```

---

## The interview answer (once you've done the above)

> "I introduced a bug by lowering the voltage ceiling, which made valid 400V
> readings get rejected. My unit test caught it immediately with a clear
> assertion failure showing a good reading marked invalid. That's the value of
> the test suite — it turned a potential silent data bug into a specific,
> reproducible failure. I traced it to the changed constant, fixed it, and the
> suite went green. That's the reproduce-diagnose-fix loop."

This directly answers "tell me about a time you debugged something" **and**
"how do your tests help catch issues" — with a real example from your own repo.
