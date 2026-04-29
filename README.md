# Bat or Brolly
🏏 A cricket-focused weather verdict app 🏏

## Architectural Design Decisions

### Open-Meteo — Weather & Geocoding API

Open-Meteo was chosen primarily because it is free and requires no registration,
which eliminated the need to store and manage API secrets. For a public-facing
app with no authentication layer, this was the appropriate choice.

Two separate API calls are made: the Geocoding API first converts a location name
into latitude and longitude coordinates, which are stored in a dictionary and
passed to the forecast API. This is necessary because Open-Meteo's forecast
endpoint requires coordinates rather than a place name.

### Application Framework — Flask

Flask was chosen because it is lightweight and unopinionated, making it well-suited
to a small, stateless, single-purpose application. Unlike Django, which ships with
an ORM, admin panel, and significant scaffolding, Flask only provides what is
needed. It also allowed the entire application to be written in Python without
introducing a separate frontend framework such as React.

### Application Structure — Monolithic

Given the scope of the application — stateless, largely static, with straightforward
logic — a monolithic structure was a deliberate choice. Splitting the app into
separate modules would have introduced unnecessary complexity without meaningful
benefit.

That said, if the app were to scale significantly — for example, adding freemium
tiers, user authentication, or a database layer — refactoring into a modular
structure would be the logical next step.

### HTTP Method — GET

The form submits via GET rather than POST. Because the app performs a purely
read-only operation with no sensitive data and no server-side state changes,
GET is the semantically correct choice. The location travels in the URL query
string, which also makes results bookmarkable and shareable — a useful side effect
for this kind of app.

### Forecast Timing — 2pm GMT

Rather than pulling the first available hourly value or using datetime.now(),
the app specifically targets the 14:00 GMT forecast. This decision was driven
by cricket domain knowledge: 14:00 is typically when 40-over matches begin,
and the point up to which 50-over matches can be postponed. Anchoring the
forecast to a meaningful match time makes the verdict significantly more
useful than a generic current-conditions check.

### Weather Variables — Temperature, Precipitation, Wind

Temperature, precipitation probability, and wind speed were chosen because they
are the primary factors that determine whether a cricket match proceeds. These
decisions were driven by subject-matter knowledge rather than purely technical
considerations — cloud cover and humidity, for example, were excluded as they
have a lower practical bearing on match decisions.

### Verdict Logic — if/elif/else

Thresholds are based on estimates of typical UK summer playing conditions.
A simple if/elif/else chain was chosen over a weighted scoring system for two
reasons: it is proportionate to the app's current scope, and it is more
performant for a lightweight web application where every request triggers
a fresh evaluation.

The thresholds and logic are acknowledged as a starting point. If the app
were to develop into a commercial product, these could be refined using
historical weather and match abandonment data to produce a more accurate model.

## Infrastructure

### Containerisation

I used Docker to ensure that whichever host is running my application will be able to run it exactly as I have locally, providing environmental parity. The containerised application ensures that whichever machine is hosting the app will be running all the same versions of the dependencies as the device it was created on, preventing any "it works on my machine"-type issues. Docker achieves this by installing all dependencies from the `requirements.txt` file during the image build, ensuring every environment runs identical versions regardless of what is installed on the host machine.

### Base Image

I used `python:3.12-slim` for two main reasons. I chose 3.12 as it is a stable, well-established release with a defined support window until 2028, meaning security patches and bug fixes are guaranteed for the foreseeable future. The newer 3.14 does not yet have that same depth of use and community support.

Because I only need my image to run my code, I opted for the `slim` variant because it does not include the build tools that come with the full image — those would be redundant, as my app does not compile anything at runtime. It also ensures I am cost-optimising my serverless compute resources by not carrying any memory overhead from unnecessary tooling.

### Gunicorn

I used Gunicorn because it can handle multiple requests simultaneously, whereas Flask's built-in server is not multi-threaded and cannot handle higher volumes of traffic. In theory this is probably not a significant issue for a portfolio app, but given how straightforward it is to install and bind Gunicorn, there was no good reason to stay with Flask's own development server — particularly given that Flask explicitly warns against using it outside of development.

I opted for 3 workers because the standard formula for worker count is (2 × CPU cores) + 1. With a 0.25 vCPU allocation, this rounds up to 1 vCPU for the purposes of the formula, giving 3 workers — this was simply a matter of following best practice.

## Infrastructure & Deployment

### ECS Fargate

Fargate was chosen because, even though it is technically more costly in terms of compute, the operational overhead saved by not having to manage the underlying infrastructure (Fargate being serverless) justifies that cost. "Serverless wherever possible" is also something AWS actively encourages across the 6 pillars of their Well-Architected Framework.

The Application Load Balancer provides a secure public-facing endpoint for all inbound internet traffic, with TLS termination and load balancing. Exposing the container directly would present a security risk, as it would be accessible to all HTTP traffic from anywhere on the internet. Using the ALB also meant that a separate reverse proxy such as NGINX was unnecessary, as TLS termination and routing are handled at the load balancer level. However, if the app were ever required to scale to handle higher traffic demands or more complex routing requirements, NGINX could be introduced.

### Terraform

I chose to manage my infrastructure through IaC with Terraform rather than via the console because it enables a fast, uniform approach to deploying reproducible infrastructure. Manual console configuration can lead to inconsistencies in the resources that are created, and makes it impossible to reliably recreate an environment from scratch.

Terraform was chosen over AWS's own CloudFormation because it is a multi-cloud tool — if I needed to migrate to another cloud provider, my Terraform resources could be adapted accordingly. Additionally, Terraform's HCL syntax is widely regarded as significantly cleaner and less verbose than CloudFormation.

Remote state in S3 with DynamoDB locking means all infrastructure state is stored in a cloud environment, providing better safety and continuity in the event of anything happening to my local machine. It also prevents state corruption from concurrent applies — if two instances of Terraform were to run simultaneously, the DynamoDB lock ensures only one can proceed at a time.

I have deliberately kept this as a dev environment given that this is a portfolio project. However, if this app were ever formally launched as a production application, a `prod.tfvars` file could easily be introduced to override key values such as CPU, memory, and task count to meet the demands of a production workload — without any changes to `main.tf`.

### CI/CD

I implemented a CI/CD pipeline to automatically deploy any changes pushed to the `main` branch, removing the risk of human error inherent in manual deployment steps — forgotten commands, incorrect ordering, or skipped stages.

In line with AWS's Well-Architected Framework, I opted to use OIDC with a dedicated IAM role rather than long-lived access keys. This follows the principle of least privilege, and OIDC specifically was chosen because it issues temporary credentials that are only valid for the duration of the job. This mitigates the risk of long-lived credentials, such as CLI access keys, being leaked or exploited.

By tagging Docker images with the commit SHA rather than overwriting `latest` on every push, I get effective version control and full traceability — any running ECS task can be traced back to the exact commit that produced it.

The infrastructure workflow runs `terraform plan` on pull requests but only executes `terraform apply` on a push to main. This ensures that infrastructure changes are reviewed and approved by a human before being applied to the live environment — particularly important given that a Terraform mistake could destroy production resources or incur significant unexpected cost.