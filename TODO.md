# Pitch Perfect — Cricket Weather App
# Build todo — work through phases in order

## Phase 1 — Build the app
- [ ] ~~Set up Flask project structure and repo~~
- [ ] ~~Integrate Open-Meteo API — fetch forecast by location~~
- [ ] ~~Write cricket conditions logic (temp, rain, wind thresholds)~~
- [ ] ~~Build simple HTML frontend — location input + verdict display~~
- [ ] ~~Test end-to-end locally~~
- [ ] ~~Build some try/except blocks into code~~
- [ ] ~~Write a README explaining the project and architectural decisions~~

## Phase 2 — Containerise
- [ ] Write a Dockerfile for the Flask app
- [ ] Build and run the image locally
- [ ] Confirm app behaves identically inside the container

## Phase 3 — Deploy to AWS
- [ ] Create ECR repository and push Docker image
- [ ] Set up ECS Fargate cluster, task definition, and service
- [ ] Configure Application Load Balancer
- [ ] Attach a custom domain (optional but worth doing)
- [ ] Smoke test the live deployment

## Phase 4 — Infrastructure as code
- [ ] Write Terraform for ECR, ECS, ALB, and IAM roles
- [ ] Parameterise environment-specific values
- [ ] Tear down manual AWS resources and redeploy via Terraform
- [ ] Store Terraform state in S3 with DynamoDB locking

## Phase 5 — CI/CD pipeline
- [ ] Set up GitHub Actions workflow file
- [ ] On push to main: build Docker image
- [ ] Push image to ECR with commit SHA as tag
- [ ] Trigger ECS service update to deploy new image
- [ ] Add a basic test step before deploy
- [ ] Confirm pipeline runs green end to end

## Stretch goals
- [ ] 5-day forecast view, not just today
- [ ] "Good for nets" vs "Good for a match" distinction
- [ ] Shareable verdict link (e.g. /verdict/london)
- [ ] Cricket ground finder for nearby venues
