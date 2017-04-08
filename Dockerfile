FROM alpine:3.5

COPY pip.requirements.txt /pip.requirements.txt
COPY src/*  /amazon_dash/

ENV TZ=Europe/Moscow

RUN apk upgrade \
    && apk --update add tzdata curl tar build-base libpcap tcpdump \
    && ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
#    && apk --update add ca-certificates openjdk7-jre \
    && apk add --no-cache python3 \
    && apk add --no-cache --virtual=build-dependencies wget \
    && wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 \
    && apk --update add nano less \
#    && apk add --no-cache git \
    && apk add libxml2 python3-dev libxslt-dev libxml2-dev bash openssl-dev libffi-dev \
    && pip install -r pip.requirements.txt \
    && apk del python3-dev libxslt-dev libxml2-dev \
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

WORKDIR "/amazon_dash"
CMD ["python3", "amazon_dash.py"]
