# amazon_dash

This is a docker container for the amazon dash button hack, I use it on my Synology.

To run it:
```
docker rm -f amazon_dash
docker run --net host -it --name amazon_dash -v $PWD/amazon-dash-private:/amazon-dash-private:ro masterandrey/amazon-dash
```

In folder `amazone-dash-private` you should have settings files `settings.json` 
and `buttons.json` (see [examples](https://github.com/masterandrey/docker-amazon-dash/tree/master/amazon-dash-private)),
`amazon-dash-hack.json` with google API credentials and
`ifttt-key.json` with 
[Maker Webhook key](https://ifttt.com/services/maker_webhooks/settings).

See details in [blog post](http://masterandrey.com/posts/en/amazon_dash/).
