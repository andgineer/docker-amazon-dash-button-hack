# amazon_dash

This is a docker container for the amazon button hack, I use it on my Synology.

To run it:
```
docker rm -f amazon_dash
docker run --net host -it --name amazon_dash -v ./amazone-dash-private:/amazone-dash-private:ro masterandrey/amazon-dash
```

In folder `amazone-dash-private` you should have `buttons.json` with the buttons list
and `amazone-dash-hack.json` with google spread credentials.

See details in [blog post](http://masterandrey.com/posts/en/amazon_dash/).
