FROM masterandrey/docker-python-base

COPY pip.requirements.txt /pip.requirements.txt
COPY src/*  /amazon_dash/

RUN pip install -r pip.requirements.txt \
    && apk del python3-dev libxslt-dev libxml2-dev \
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

WORKDIR "/amazon_dash"
CMD ["python3", "amazon_dash.py"]
