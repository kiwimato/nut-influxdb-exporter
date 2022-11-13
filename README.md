# nut-influxdb-exporter
## :warning: this code is is no longer maintained because Telegraf added NUT support [in this PR](https://github.com/influxdata/telegraf/pull/9890/files#diff-60ad28a279b042acced351b6dd19a9a339d8349d6ab603054345bd23bd279462)
## However, if you don't use Telegraf I recommend looking at these 2 forks:
* https://github.com/jwillmer/nut-influxdbv2
* https://github.com/dbsqp/nut-influxdbv2

If you use Grafana + Unraid, make sure to checkout `Unraid System Dashboard New-1577093376607.json`. 
While some graphs might need some tweaking for your particular setup, it's better than nothing.

You can find the docker image here:
https://hub.docker.com/r/maihai/nut-influxdb-exporter

# Contributions
Please create a PR to `develop` branch since GitHub actions doesn't offer an easy way to pass secrets to PRs from forks yet.
