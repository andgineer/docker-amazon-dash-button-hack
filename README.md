[![Build Status](https://travis-ci.org/masterandrey/docker-amazon-dash-button-hack.png)](https://travis-ci.org/masterandrey/docker-amazon-dash-button-hack)

This is a [Docker Hub container](https://hub.docker.com/r/masterandrey/docker-amazon-dash-button-hack/) 
for the Amazon Dash Button hack.
It can write to Google Sheets, Google Calendar and fire event in [IFTTT](https://ifttt.com).

I use it on my [Synology](https://www.synology.com).

To run it:
```
docker rm -f amazon_dash
docker run --net host -it --name amazon_dash -v $PWD/amazon-dash-private:/amazon-dash-private:ro masterandrey/docker-amazon-dash-button-hack
```

In folder `amazone-dash-private` you should have:

* settings `settings.json` 
* buttons list `buttons.json` 
* `amazon-dash-hack.json` with google API credentials [Google Sheets](https://console.developers.google.com/start/api?id=sheets.googleapis.com), [Google Calendar](https://console.developers.google.com/start/api?id=calendar)
* `ifttt-key.json` with [Maker Webhook key](https://ifttt.com/services/maker_webhooks/settings)

[Examples of this files](https://github.com/masterandrey/docker-amazon-dash-button-hack/tree/master/amazon-dash-private).

There are your secrets in that folder so you have to **create all this files by youself** from examples
you see by link above.

See details in [Smart wifi button and Docker on Synology (Amazon Dash Button hack)](http://masterandrey.com/posts/en/amazon_dash_button_hack/).
