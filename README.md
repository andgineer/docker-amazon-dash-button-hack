[![Build Status](https://github.com/andgineer/docker-amazon-dash-button-hack/workflows/ci/badge.svg)](https://github.com/andgineer/docker-amazon-dash-button-hack/actions)

This is a [Docker Hub container](https://cloud.docker.com/repository/registry-1.docker.io/andgineer/amazon-dash-button-hack) 
for the Amazon Dash Button hack.

It sniff network to catch Amazon Buttons communications with Amazon. And thus detects press on the buttons.

It can write to Google Sheets, Google Calendar and fire event in [IFTTT](https://ifttt.com).

I use it on my [Synology](https://www.synology.com).

To run it:
```
docker run \
    --net host \
    -it \
    --rm \
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro \
    andgineer/amazon-dash-button-hack
```

In folder `amazone-dash-private` you should have:

* settings `settings.json` 
* buttons list `buttons.json` 
* `amazon-dash-hack.json` with google API credentials [Google Sheets](https://console.developers.google.com/start/api?id=sheets.googleapis.com), [Google Calendar](https://console.developers.google.com/start/api?id=calendar)
* `ifttt-key.json` with [Maker Webhook key](https://ifttt.com/services/maker_webhooks/settings)

[Examples of this files](https://github.com/andgineer/docker-amazon-dash-button-hack/tree/master/amazon-dash-private).

There are your secrets in that folder so you have to **create all this files by youself** from examples
you see by link above.

See details in [Smart wifi button and Docker on Synology (Amazon Dash Button hack)](https://sorokin.engineer/posts/en/amazon_dash_button_hack/).

## MacOS and Windows

You cannot sniff network from Docker containers running on MacOS and Windows because they do not run
docker demon natively but use Virtual Machine to run it.

So to debug on MacOS and Windows: 

    . ./activate.sh
    sudo python src/amazon_dash.py

## Developers

We use `collections.abc` so min Python3.10
