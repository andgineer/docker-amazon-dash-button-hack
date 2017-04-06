FROM alpine:3.5

COPY pip.requirements.txt /pip.requirements.txt

RUN apk --update add curl ca-certificates tar build-base \
    && apk --update add openjdk7-jre \
    && apk add libpcap tcpdump \
    && apk add --no-cache python3 \
    && apk add --no-cache --virtual=build-dependencies wget \
    && wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 \
    && apk --update add nano less \
    && apk add --no-cache git \
    && apk upgrade \
    && apk add libxml2 python3-dev libxslt-dev libxml2-dev bash openssl-dev libffi-dev \
    && pip install -r pip.requirements.txt \
    && apk del python3-dev libxslt-dev libxml2-dev \
    && rm -rf ~/.pip/cache/
    
COPY amazon_dash.py  /
COPY google_sheet.py  /

CMD ["python3", "amazon_dash.py"]
