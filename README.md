# amazon_dash

Image for [Docker hub](https://hub.docker.com/r/masterandrey/amazone-dash/)

This is a Dockerfile for the hack described in [Amazone dash hack](http://masterandrey.com/posts/en/amazone_dash/)

To run it:
```
docker rm -f amazon_dash; docker run --net host -it --name amazon_dash masterandrey/amazone-dash
```
