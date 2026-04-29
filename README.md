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

I used Docker to ensure that whichever local host is utilising my application will be able to run it exactly as I have locally (providing environmental parity). The containerised application ensures that whichever machine is hosting my application will be running all the same versions of the dependencies as the device the app was created on, preventing any "it works on my machine"-type issues. This is achieved through Docker utilising the 'requirements.txt' file in my codebase.

### Base Image

I utilised python 12-slim for two main reasons. I went for 3.12 as it has LTS, with a wealth of support available, both officially in terms of patching, bug fixes etc, and also in terms of community support via forums and message boards. Where as the newer 3.14 does not quite have that depth of use and support.

Because I only need my image to run my code, I opted for the 'slim' image because it does not include all of the build tools the full image comes with, as these would be redundant, as my app does not compile anything at runtime. It will also ensure that I am cost-optimising my serverless compute resources by not having any memory used by redundant tooling.

### Gunicorn

I used Gunicorn because it can handle multiple requests at the same time, where as the flask server is not multi-threaded and so cannot handle higher volumes of requests. In theory this is probably not a huge issue for a portfolio app, but given how easy it is to install and bind gunicorn, it made no sense to stay with the flask's own production server, with it's known limitations and the fact that Flask explicitly saying not to use it outside of development.
I opted for 3 "workers" because the general formula for number of workers is 2 per CPU core, +1. Because I have opted for a 0.25 vCPU, this needs to be rounded up to 1vCPU (for the purposes of the formula) - Therefore this was simply a matter of following best practice.

## Infra&Deployment

### ECS Fargate

Fargate was chosen specifically because, even though it is technically more costly in terms of compute, the time I don't have to invest in maintaining the infrastructure (as Fargate is serverless) makes up for that cost-saving. Also, "serverless wherever possible" is effectively an unwritten rule of AWS, and something they actively encourage in the 6 pillars of thier Well Architected Framework.
The ALB gives me a layer of security by providing public facing endpoint for all inbound internet traffic, with its TLS termination, and load balancing. If the container was exposed directly this would be a security risk as the container would be exposed to all HTTP traffic from 'anywhere'. As an aside, using the ALB also meant that I didn't have to configure a reverse proxy server, such as NGINX as TLS termination and routing is handled by the ALB. However, if the app was ever required to scale up to cope with higher traffic demands, or more complex routing was required, NGINX could be introduced.

### Terraform

I chose to use Terraform to manage my infrastructure, through IaC instead of via the console because it enabled a fast, uniformed approach to deploying reproducible infrastructure. Where as the console can lead to inconsistencies in resources being spun up due to it's manual configuration process. 
Terraform was used as it is a multi-cloud tool - So if I needed to move to another cloud provider, then I could still utilise my Terraform resources, albeit with some tweaking, on top of that, the syntax is widely viewed as much cleaner and less verbose than CloudFormation.

A Remote state in S3 with DB Locking meant that I would be able to store all of my version control/IaC deployment records in a clouded environment for better safety and improved continuity, in the event of anything happening to my infrastructure. It also means that if there are any concurrent applies, then the DB will be Locked, preventing state corruption.

I have purposefully kept this as a dev environment as this is a portfolio project. However, if I was looking to formally launch this as a production app, I could easily introduce a prod.tfvars file that would be used to override key values such as higher vCPU and Memory resources that would be required in a production environment.

### CI/CD

I implemented a CI/CD pipeline because it will allow me to automatically deploy any changes that are pushed to my 'main' branch (ie, once those deployments are ready for prod). 

Per AWS's Well Architected Framework, I opted to use OICD with an IAM Role. This is inline with the principle of least priviledge, however the OICD specifically was chosen as it creates temporary credentials, that are only valid until the job has executed. This mitigates the risk of long-lived credentials, such as CLI access keys, being exploited.

By using the SHA tags I get an effective version control, instead of having to overwrite "latest" every time, it also provides traceability, via the corresponding ecs -> sha tags

By only running 'apply' on the push to main, it ensures that only a reviewed and approved (by a human) version of the commit is submitted in to the live environment. This is especially important in terms of infrastructure; where a mistake could destroy production resources, or incur a high monetary cost.