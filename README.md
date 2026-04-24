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