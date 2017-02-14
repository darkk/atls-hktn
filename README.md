[The second Russian hackathon on Internet measurements](https://www.facebook.com/events/1426934460659344/)

Original goal: measure latency between geographically close points and pinpoint
abnormally high latencies (bad peering?) compared to speed of light in fiber.

The goal was shifted to replace active measurements with historical
measurements analytics, modified goal was to find latency outliers between two
geocoded endpoints, especially violations of speed of light (showing geocoding
incorrectness).

Assumptions:

1. All IP addresses within /24 are quite close geographically
2. Geolocation data for RIPE Atlas probes from YYYYMMDD.json may be ultimately
   trusted and is almost static

So far these assumptions turned out to be non 100%-true.

[Probe #27782](https://atlas.ripe.net/probes/27782/#!tab-network) and
[probe #6254](https://atlas.ripe.net/probes/6254/#!tab-network) are within same
/29 but they're 350 km away, so assumption of near-zero latency between these
two hosts is wrong and calculations assuming near-zero latency between hosts in
same /24 lead to contradiction with speed of light being limited.

Also, some probes have their "latency-based" location quite far from "declared"
location. Some of these probes are "travelling", some estimates of
latency-based location may be wrong due to wrongly located destination
locations (that are based on /24 locality assumption) and so on, some of these
probes can be seen in [fishy.ipynb](fishy.ipynb).

Latency measurement may be used to find outliers in geolocation, but common
factor of ~2x difference between actual RTT and RTT estimated with speed of
light in fiber and traversed distance makes it not so precise.
