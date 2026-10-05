# Git workflow

Covers the JD requirement: *"branching strategies and pull requests, with
ability to resolve merge conflicts."* Do this once so you can speak to it from
real experience.

## Branching + PR flow

```bash
# 1. Start a feature branch off main
git checkout -b feature/add-humidity-check

# 2. Make a change (e.g. add a humidity validator), commit
git add .
git commit -m "Add humidity range validation"

# 3. Push the branch
git push origin feature/add-humidity-check

# 4. Open a Pull Request on GitHub (feature → main)
#    → CI runs automatically on the PR (all test layers)
#    → review, then Merge once green
```

## Practicing a merge conflict (optional, 10 min)

A merge conflict happens when two branches change the same lines. To create and
resolve one on purpose:

```bash
# On main, change VOLTAGE_MAX to 1200
git checkout main
# edit validators.py: VOLTAGE_MAX = 1200.0
git commit -am "Raise voltage ceiling to 1200 on main"

# On a branch made earlier, change the SAME line to 1100
git checkout -b feature/other-ceiling
# edit validators.py: VOLTAGE_MAX = 1100.0
git commit -am "Set voltage ceiling to 1100"

# Try to merge main in → conflict on that line
git merge main
```

Git marks the conflict like this:

```
<<<<<<< HEAD
VOLTAGE_MAX = 1100.0
=======
VOLTAGE_MAX = 1200.0
>>>>>>> main
```

**Resolve it** by editing the file to the value you want, removing the marker
lines, then:

```bash
git add app/validators.py
git commit                 # completes the merge
```

## Interview line

> "I work in feature branches, open PRs so CI runs before anything merges, and
> I've resolved merge conflicts — Git marks the conflicting lines and you pick
> the correct resolution, stage it, and complete the merge. In my project, the
> PR is where the whole test suite acts as the gate before code reaches main."
