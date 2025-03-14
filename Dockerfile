FROM andgineer/lean-python

COPY requirements.txt requirements.txt

RUN uv pip install -r requirements.txt

COPY src/*  ./

CMD ["amazon_dash.py"]
