[![Build Status](https://github.com/andgineer/docker-amazon-dash-button-hack/workflows/ci/badge.svg)](https://github.com/andgineer/docker-amazon-dash-button-hack/actions)[![Docker Automated build](https://img.shields.io/docker/image-size/andgineer/amazon-dash-button-hack)](https://hub.docker.com/r/andgineer/amazon-dash-button-hack)

This is a [Docker Hub container](https://hub.docker.com/r/andgineer/amazon-dash-button-hack)
for the [Amazon Dash Button hack](https://sorokin.engineer/posts/en/amazon_dash_button_hack.html).

It sniffs the network to intercept Amazon Button communications with Amazon,
thereby detecting button presses.

It can write to Google Sheets, Google Calendar and fire event in [IFTTT](https://ifttt.com).

I use it on my [Synology](https://www.synology.com) for
[IoT calendar](https://sorokin.engineer/posts/en/iot_calendar_synology.html).

To run the container on Linux:
```
docker run \
    --net host \
    -it \
    --rm \
    -v $PWD/../amazon-dash-private:/amazon-dash-private:ro \
    andgineer/amazon-dash-button-hack
```

In folder `../amazone-dash-private` you should have:

* settings [`settings.json`](https://andgineer.github.io/docker-amazon-dash-button-hack/settings/)
* buttons list `buttons.json`
* `amazon-dash-hack.json` with google API credentials [Google Sheets](https://console.developers.google.com/start/api?id=sheets.googleapis.com), [Google Calendar](https://console.developers.google.com/start/api?id=calendar)
* `ifttt-key.json` with [Maker Webhook key](https://ifttt.com/services/maker_webhooks/settings)

[Examples of this files](https://github.com/andgineer/docker-amazon-dash-button-hack/tree/master/amazon-dash-private).
- this is folder `amazone-dash-private` of the repo.

See details in [User manual](https://sorokin.engineer/posts/en/amazon_dash_button_hack_install.html).

## MacOS and Windows

You cannot sniff network from Docker containers running on MacOS and Windows because they do not run
docker demon natively but use Virtual Machine to run it.

So to debug on MacOS and Windows:

    . ./activate.sh
    sudo python src/amazon_dash.py

## Developers

We use `collections.abc` so min Python3.10

[API docs](https://andgineer.github.io/docker-amazon-dash-button-hack/docstrings/)

# Scripts
    make help
