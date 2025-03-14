FROM andgineer/lean-python

COPY requirements.txt requirements.txt

RUN uv pip install -r requirements.txt \
    && apk del python3-dev libxslt-dev libxml2-dev

COPY src/*  ./

CMD ["python3", "amazon_dash.py"]
