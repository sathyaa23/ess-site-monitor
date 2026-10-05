# AWS deployment (deploy-ready)

This project is **built to deploy to AWS**. The Docker image and the CI pipeline's
ECR-push step are real and correct. This doc explains the full path and how the
JD's AWS services (S3, EC2, IAM) fit.

> **Honest framing for the interview:** "I containerized the app and set up the
> pipeline to push to ECR — the deploy path is built. I haven't run it against a
> live AWS account with billing, but I understand each step and where S3, EC2,
> and IAM come in." This is true and unbluffable — do NOT claim a live production
> deploy you didn't run.

---

## How the JD's AWS services map to this app

| Service | Role in deploying this app |
|---------|----------------------------|
| **IAM** | Roles/policies granting the pipeline permission to push to ECR and the EC2 host permission to pull the image. Least-privilege = a real security concern. |
| **ECR** | Elastic Container Registry — stores the built Docker image (the artifact). |
| **EC2** | A compute instance that pulls the image and runs the container. |
| **S3** | Where you'd store telemetry data, logs, or test artifacts (e.g. Playwright screenshots on failure). |

## The deploy path

```
docker build  →  push to ECR  →  EC2 pulls image  →  docker run  →  live
                     ↑                                    ↑
                 IAM lets CI push              IAM lets EC2 pull
```

## To run it live (steps)

1. **Create an ECR repository:**
   ```bash
   aws ecr create-repository --repository-name ess-site-monitor
   ```

2. **Add IAM credentials as GitHub repo secrets:**
   `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (from an IAM user with
   `AmazonEC2ContainerRegistryPowerUser` policy). The CI's ECR-push step is
   already written to activate once these exist.

3. **Push happens automatically** on the next merge to `main` (see the
   "Push image to Amazon ECR" step in `.github/workflows/ci.yml`).

4. **Run on EC2:**
   ```bash
   # on the EC2 instance (with an IAM role allowing ECR pull)
   aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   docker pull <account>.dkr.ecr.us-east-1.amazonaws.com/ess-site-monitor:latest
   docker run -d -p 80:8000 <account>.dkr.ecr.us-east-1.amazonaws.com/ess-site-monitor:latest
   ```

## Why it's gated in CI

The ECR-push step has `if: ${{ secrets.AWS_ACCESS_KEY_ID != '' }}` — so the
pipeline stays green for anyone cloning the repo without AWS credentials, and
only attempts a real push when credentials are present. That's a deliberate
design choice, and a good thing to mention: pipelines shouldn't fail just
because optional infrastructure isn't configured.
