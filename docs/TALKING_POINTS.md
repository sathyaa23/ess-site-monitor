# Interview talking points (honest, per component)

The rule: **build it, run it, understand it, then claim it.** Everything below is
claimable ONLY after you've actually run it. Run the project first.

---

## The 30-second project pitch

> "I built ESS Site Monitor — a FastAPI service that validates battery telemetry
> and flags anomalies. I tested it in three layers: pytest units on the
> validation logic, integration tests on the API with TestClient, and end-to-end
> browser tests with both Playwright and Selenium. All of it runs in a GitHub
> Actions pipeline that gates a Docker build, and it's packaged to deploy to AWS.
> I built it specifically to get hands-on with your exact stack."

---

## What you CAN claim (after running it)

| Component | Honest claim |
|-----------|--------------|
| pytest unit tests | "I wrote parametrized unit tests on the validation logic." ✅ |
| Integration tests | "I tested the API with FastAPI's TestClient, asserting status codes." ✅ |
| Playwright | "I wrote E2E browser tests driving the dashboard." ✅ |
| Selenium | "I wrote the same flows in Selenium — I can speak to the differences (explicit waits vs Playwright's auto-wait)." ✅ |
| GitHub Actions | "I built a 3-job pipeline: fast tests → E2E → package, gated so each stage only runs if the prior passed." ✅ |
| Docker | "I wrote a multi-stage Dockerfile with a healthcheck, running as non-root, and built + ran the image." ✅ |
| Python packaging | "It's packaged with pyproject.toml — `python -m build` produces a wheel." ✅ |
| Debugging | "I introduced a bug, my tests caught it, I traced and fixed it." ✅ (after doing BUGFIX.md) |
| Git/PR | "Feature branches, PRs with CI as the gate, and I've resolved merge conflicts." ✅ (after doing GIT_WORKFLOW.md) |

## Where to stay honest (the boundaries)

| Topic | Honest boundary |
|-------|-----------------|
| AWS | "The deploy path is built — ECR push in CI, documented EC2/IAM steps. I haven't run it against a live billed AWS account yet." Don't claim a live prod deploy. |
| Kubernetes | "Not in this project. I understand it orchestrates containers above the Docker level — conceptual, not hands-on." |
| Jenkins | "I used GitHub Actions; Jenkins does the same job. Concepts transfer, haven't written a Jenkinsfile." |
| Scale/production | "This is a reference project with an in-memory store, not a production system with a real DB and load." |

## If they ask "did you build this for us?"

Be honest — it's a strength, not a weakness:

> "Yes. I saw the stack in the JD — pytest, Playwright, Selenium, Docker, CI/CD —
> and rather than just claim familiarity, I built a project to get genuine
> hands-on experience with them. I'd rather show you working code I understand
> than list buzzwords."

A Lead SWE respects that far more than a candidate pretending years of experience.

## The mindset

You have ~2 years of data engineering, not QA. That's fine — this is an
internship. The pitch is: **"real foundation + I close gaps fast, here's proof."**
This project IS the proof.
