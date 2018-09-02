FROM masterandrey/docker-python-base

COPY amazon_dash/requirements.txt /requirements.txt

RUN pip install -r requirements.txt \
    && apk del python3-dev libxslt-dev libxml2-dev \
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

COPY amazon_dash/*  /amazon_dash/

WORKDIR "/amazon_dash"
CMD ["python3", "amazon_dash.py"]
