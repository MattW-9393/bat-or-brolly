# BAT OR BROLLEY
Cricket-focused weather app

## Architecture Design Decisions

Open-Meteo — Weather & Geocoding API

I chose open-meteo primarily because it is free, and does not require registration. 
That meant that there was less of a risk around needing to safely store secrets.

I used the Geocoding API as Open-Meteo's api requires a longitude and latitude value, therefore by using the Geocoding API I could extract those values and provide them to the API via a dictionary that my get_weather() function extracts. 

----------

Application Framework — Flask

I chose flask as it was the best python framework for a stateless web app. Because it is lightweight and un-opinionated (versus Django which comes with ORM and admin functionality). 
It enabled me to write full-stack code all in one place, without requiring the number of dependencies something like a REACT app would.

----------

Application Structure — Monolithic

As the app logic is relatively straightforward, it would have been overkill to set up seperate modules. In terms of apps, it's stateless and the majority of the app is static. Outside of seperating concerns in terms of back end and front end code. Therefore, having a more monolithic structure reduces the complexity. 

That being said, if I wanted to significantly scale the app, creating freemium tiers which subsequently use auth etc, at that point I would have to refactor and create modules, but for now it makes sense for it to be monolithic.

----------

HTTP Method — GET

I used GET because the site is not sending, or retrieving any sensitive data. The API has no secret, it's not even registered, so it makes sense for it to all be rendered and managed in the URL. Nothing is happening with the data in the server, its purely a "Read" operation

----------

Forecast Timing — 2pm GMT

I'm actually pulling "2pm GMT" [14]. However, this isn't a random variable. This decision was driven by years or playing cricket, and awareness of match start times.
14:00 is usually the point at which 40 over cricket matches start, and 50 over cricket matches can be postponed until. Therefore it made sense to specifically select a time-slot relative to actual cricket matches
as opposed to either [0] or setting a date.time.now() variable.

Weather Variables — Temperature, Precipitation, Wind

I chose, temperature, wind and precipitation %, purely because in terms of assessing weather conditions for cricket, those are the most obvious, and have the highest bearing on if a match is called off.
These architectural decisions were driven largely by subject-matter knowledge of the target audience, as opposed to purely technical decisions.
----------

Verdict Logic — if/elif/else

The thresholds were estimates of what is considered a pleasant summer conditions in the UK.
If/elif/else seemed sensible as the app is largely a gimmick app. It was easy to implement and programmatically requires less "horespower" than a scoring system. This is a web app so performance does play some part.

However, these decisions were made based on the app being a scaffold to demonstrate architectural and infrastructure support abilities. If the App was popular and was shown to be a potential commercial product, these aspects can be refactored
and historical weather data can be included to also help determine the liklihood of play going ahead.