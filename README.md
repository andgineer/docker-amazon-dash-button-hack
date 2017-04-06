# amazon_dash

Image for [Docker hub](https://hub.docker.com/r/masterandrey/amazon-dash/)

This is a Dockerfile for the hack described in [Amazon dash hack](http://masterandrey.com/posts/en/amazon_dash/)

To run it:
```
docker rm -f amazon_dash; docker run --net host -it --name amazon_dash masterandrey/amazon-dash
```
