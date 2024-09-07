FROM andgineer/lean-python

COPY requirements.txt /requirements.txt

RUN uv pip install -r requirements.txt \
    && apk del python3-dev libxslt-dev libxml2-dev \
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

COPY src/*  /amazon_dash/

WORKDIR "/amazon_dash"
CMD ["python3", "amazon_dash.py"]
